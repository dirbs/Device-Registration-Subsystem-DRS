"""
DRS report resource package.
Copyright (c) 2018-2020 Qualcomm Technologies, Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
    The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
    Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
    This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import json
import os

from flask import Response, send_file
from flask_restful import Resource
from flask_apispec import marshal_with, doc, MethodResource, use_kwargs
from flask_babel import lazy_gettext as _

from app import app, db
from app.api.v1.helpers.error_handlers import REG_NOT_FOUND_MSG, REPORT_NOT_FOUND_MSG, \
    REPORT_NOT_ALLOWED_MSG, DEREG_NOT_FOUND_MSG
from app.api.v1.helpers.response import MIME_TYPES, CODES
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.models.deregdetails import DeRegDetails
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.schema.common import ErrorResponse, SuccessResponse, \
    DashboardReportsArgs, UserTypes, ImieReportsArgsGet, ImieReportsArgsPost


class ImeiReport(MethodResource):
    """Class for handling Report Routes."""

    @doc(description='Get Imei report', tags=['Imei-Reports'])
    @marshal_with(SuccessResponse, code=200, description='On success(Report generated successfully)')
    @marshal_with(ErrorResponse, code=500, description='On error(Un-Identified Error)')
    @marshal_with(ErrorResponse, code=400, description='On error(Bad argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error(Request content not found)')
    @use_kwargs(ImieReportsArgsGet().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """GET method handler, return registration report."""
        for key, value in kwargs.items():
            if value is None:
                res = {'error': ['{0} is required'.format(key)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=422, mimetype='application/json')
        user_type = kwargs.get('user_type')
        request_type = kwargs.get('request_type')
        request_id = kwargs.get('request_id')
        user_id = kwargs.get('user_id')
        if request_type == 'registration_request':
            if not request_id.isdigit() or not RegDetails.exists(request_id):
                return Response(app.json_encoder.encode(REG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            req = RegDetails.get_by_id(request_id)
            if not req.report:
                return Response(app.json_encoder.encode(REPORT_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            report_allowed = True if user_type == 'reviewer' or \
                                     (req.user_id == user_id and req.report_allowed) else False
            if report_allowed:
                if user_type == 'reviewer':
                    report_name = req.report
                else:
                    report_name = 'user_report-{}'.format(req.report)
                report = os.path.join(app.config['DRS_UPLOADS'], req.tracking_id, report_name)
                return send_file(report)
            else:
                return Response(app.json_encoder.encode(REPORT_NOT_ALLOWED_MSG),
                                status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        else:
            if not request_id.isdigit() or not DeRegDetails.exists(request_id):
                return Response(app.json_encoder.encode(DEREG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            req = DeRegDetails.get_by_id(request_id)
            if not req.report:
                return Response(app.json_encoder.encode(REPORT_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            report_allowed = True if user_type == 'reviewer' or \
                                     (req.user_id == user_id and req.report_allowed) else False
            if report_allowed:
                if user_type == 'reviewer':
                    report_name = req.report
                else:
                    report_name = 'user_report-{}'.format(req.report)
                report = os.path.join(app.config['DRS_UPLOADS'], req.tracking_id, report_name)
                return send_file(report)
            else:
                return Response(app.json_encoder.encode(REPORT_NOT_ALLOWED_MSG),
                                status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))


class GetDashBoardReports(MethodResource):
    """Class for returning dashboard reports."""

    @doc(description='Get Dashboard Reports', tags=['Dashboard'])
    @marshal_with(SuccessResponse, code=200, description='On success(Report generated successfully)')
    @marshal_with(ErrorResponse, code=500, description='On error(Un-Identified Error)')
    @marshal_with(ErrorResponse, code=400, description='On error(Bad argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error(Request content not found)')
    @use_kwargs(DashboardReportsArgs().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """GET method handler for dashboard reports."""
        for key, value in kwargs.items():
            if value is None:
                res = {'error': ['{0} is required'.format(key)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=422, mimetype='application/json')

        user_id = kwargs.get('user_id')
        user_type = kwargs.get('user_type')
        response_data = {
            "user_id": user_id,
            "user_type": user_type
        }
        if user_type == UserTypes.REVIEWER.value:
            registraton_info = RegDetails.get_dashboard_report(user_id, user_type)
            de_registraton_info = DeRegDetails.get_dashboard_report(user_id, user_type)
            response_data['registration'] = registraton_info
            response_data['de-registration'] = de_registraton_info
        elif user_type in [UserTypes.IMPORTER.value, UserTypes.INDIVIDUAL.value]:
            registraton_info = RegDetails.get_dashboard_report(user_id, user_type)
            response_data['registration'] = registraton_info
        elif user_type == UserTypes.EXPORTER.value:
            de_registraton_info = DeRegDetails.get_dashboard_report(user_id, user_type)
            response_data['de-registration'] = de_registraton_info

        response = Response(json.dumps(response_data), status=CODES.get("OK"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        return response


class SetImeiReportPermissions(MethodResource):
    """Class for setting reports permissions."""

    @doc(description='Set Permission for Imei-report', tags=['Imei-Reports'])
    @marshal_with(SuccessResponse, code=200, description='On success(Report permissions set successfully)')
    @marshal_with(ErrorResponse, code=500, description='On error(Un-Identified Error)')
    @marshal_with(ErrorResponse, code=400, description='On error(Bad argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error(Request content not found)')
    @use_kwargs(ImieReportsArgsPost().fields_dict, locations=['json'])
    def post(self, **kwargs):
        """Post method handler, set report permissions."""
        for key, value in kwargs.items():
            if value is None:
                res = {'error': ['{0} is required'.format(key)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=422, mimetype='application/json')
        user_type = kwargs.get('user_type')
        request_type = kwargs.get('request_type')
        request_id = kwargs.get('request_id')
        user_id = kwargs.get('user_id')
        if request_type == 'registration_request':
            if not request_id.isdigit() or not RegDetails.exists(request_id):
                return Response(app.json_encoder.encode(REG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            req = RegDetails.get_by_id(request_id)
            if not req.report:
                return Response(app.json_encoder.encode(REPORT_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            if user_type == 'reviewer' and req.reviewer_id == user_id:
                response = RegDetails.toggle_permission(req)
                response = {'message': 'The permission to view report is changed', 'value': response}
                return Response(json.dumps(response), status=CODES.get("OK"),
                                 mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:
                return Response(app.json_encoder.encode(REPORT_NOT_ALLOWED_MSG),
                                status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        else:
            if not request_id.isdigit() or not DeRegDetails.exists(request_id):
                return Response(app.json_encoder.encode(DEREG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            req = DeRegDetails.get_by_id(request_id)
            if not req.report:
                return Response(app.json_encoder.encode(REPORT_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            if user_type == 'reviewer' and req.reviewer_id == user_id:
                response = DeRegDetails.toggle_permission(req)
                response = {'message': 'The permission to view report is changed', 'value': response}
                return Response(json.dumps(response), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:
                return Response(app.json_encoder.encode(REPORT_NOT_ALLOWED_MSG),
                                status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
