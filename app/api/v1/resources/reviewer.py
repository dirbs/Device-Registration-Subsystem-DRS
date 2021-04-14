"""
DRS reviewer resource package.
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
# pylint: disable=too-many-nested-blocks
import json
import datetime

from flask import Response
from sqlalchemy.exc import SQLAlchemyError
from flask_apispec import marshal_with, doc, MethodResource, use_kwargs
from flask_babel import lazy_gettext as _

from app import app, GLOBAL_CONF
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.models.notification import Notification
from app.api.v1.models.deregdetails import DeRegDetails
from app.api.v1.models.regdevice import RegDevice
from app.api.v1.models.deregdevice import DeRegDevice
from app.api.v1.models.devicetype import DeviceType
from app.api.v1.models.technologies import Technologies
from app.api.v1.models.approvedimeis import ApprovedImeis
from app.api.v1.models.devicequota import DeviceQuota as DeviceQuotaModel
from app.api.v1.models.documents import Documents as ReqDocument
from app.api.v1.models.association import ImeiAssociation
from app.api.v1.schema.common import RequestStatusTypes
from app.api.v1.schema.reviewer import UpdateReviewerArgs, SuccessResponse, SubmitSuccessResponse, ErrorResponse, \
    SectionReviewArgs, DeviceQuota as DeviceQuotaSchema, DeviceQuotaArgs, RequestTypes, DevicesDescription, \
    IMEIRegStatus, IMEIRegStatusArgs, Documents, DocumentsApiArgs, DeviceDescriptionArgs, Sections as SectionSchema, \
    SectionsArgs, SectionTypes, IMEIClassification as IMEIClassificationSchema, UnAssignReviewerArgs, SubmitReviewArgs
from app.api.v1.models.eslog import EsLog
from app.api.v1.models.status import Status


class AssignReviewer(MethodResource):
    """Class for managing Reviewer Route Methods."""

    @doc(description='Assign reviewer to the request', tags=['Reviewers'])
    @marshal_with(SuccessResponse, code=201, description='On success(Request assigned to reviewer)')
    @marshal_with(ErrorResponse, code=500, description='On error(Un-Identified Error)')
    @marshal_with(ErrorResponse, code=400, description='On error(Bad argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Request content not found)')
    @use_kwargs(UpdateReviewerArgs().fields_dict, locations=['json'])
    def put(self, **kwargs):
        """PUT Methods handler for Reviewer Routes."""
        for key, value in kwargs.items():
            if value is None:
                res = {'error': ['{0} is required'.format(key)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=422, mimetype='application/json')

        request_id = kwargs.get('request_id')
        reviewer_id = kwargs.get('reviewer_id')
        reviewer_name = kwargs.get('reviewer_name')
        request_type = kwargs.get('request_type')

        if request_type == RequestTypes.REG_REQUEST.value:  # if it is a registration request
            if RegDetails.exists(request_id):
                request = RegDetails.get_by_id(request_id)

                if request.status == 3 and request.report is not None:
                    assigned = RegDetails.update_reviewer_id(reviewer_id, reviewer_name, request_id)
                    if assigned is True:
                        res = {'message': 'reviewer {rev_id} assigned to request {req_id}'.format(
                            rev_id=reviewer_id, req_id=request_id)}

                        # Log Data
                        description = 'Reviewer {rev_name} assigned to registration request id: {req_id}'.format(
                            rev_name=kwargs['reviewer_name'], req_id=request.id)

                        log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="Registration Request",
                                                       request_details=request,
                                                       status=Status.get_status_type(request.status),
                                                       description=description)
                        EsLog.insert_log(log)

                        return Response(json.dumps(SuccessResponse().dump(res).data),
                                        status=201, mimetype='application/json')
                    else:
                        res = {'error': ['Unable to assign already assigned request']}
                        return Response(json.dumps(ErrorResponse().dump(res).data),
                                        status=400, mimetype='application/json')
                else:
                    res = {'error': [_('incomplete request %(id)s can not be assigned/reviewed', id=request_id)]}
                    return Response(app.json_encoder.encode(res),
                                    status=400, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')
        else:  # if it is a de-registration request
            if DeRegDetails.exists(request_id):
                request = DeRegDetails.get_by_id(request_id)

                if request.status == 3 and request.report is not None:
                    assigned = DeRegDetails.update_reviewer_id(reviewer_id, reviewer_name, request_id)
                    if assigned is True:
                        res = {'message': 'reviewer {rev_id} assigned to request {req_id}'.format(
                            rev_id=reviewer_id, req_id=request_id)}

                        # Log data
                        description = 'Reviewer {rev_name} assigned to de-registration request id: {req_id}'.format(
                            rev_name=kwargs['reviewer_name'], req_id=request.id)

                        log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="De Registration Request",
                                                       request_details=request,
                                                       status=Status.get_status_type(request.status),
                                                       description=description)
                        EsLog.insert_log(log)

                        return Response(json.dumps(SuccessResponse().dump(res).data),
                                        status=201,
                                        mimetype='application/json')
                    else:
                        res = {'error': ['Unable to assign reviewer to already assigned request']}
                        return Response(json.dumps(ErrorResponse().dump(res).data),
                                        status=400, mimetype='application/json')
                else:
                    res = {'error': [_('incomplete request %(id)s can not be assigned/reviewed', id=request_id)]}
                    return Response(app.json_encoder.encode(res),
                                    status=400, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')


class UnAssignReviewer(MethodResource):
    """Class for managing un-assign reviewer"""

    @doc(description='Un-assign a request', tags=['Reviewers'])
    @marshal_with(SuccessResponse, code=201, description='On success(Request assigned to reviewer)')
    @marshal_with(ErrorResponse, code=500, description='On error(Un-Identified Error)')
    @marshal_with(ErrorResponse, code=400, description='On error(Bad argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Request content not found)')
    @use_kwargs(UnAssignReviewerArgs().fields_dict, locations=['json'])
    def put(self, **kwargs):
        """PUT method handler for un-assigning request review."""
        for key, value in kwargs.items():
            if value is None:
                res = {'error': ['{0} is required'.format(key)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=422, mimetype='application/json')

        request_id = kwargs.get('request_id')
        reviewer_id = kwargs.get('reviewer_id')
        request_type = kwargs.get('request_type')

        if request_type == RequestTypes.REG_REQUEST.value:
            if RegDetails.exists(request_id):
                request = RegDetails.get_by_id(request_id)
                if request.reviewer_id == reviewer_id:
                    RegDetails.un_assign_request(request_id)
                    res = {
                        'message': 'Successfully un-assigned the request'
                    }

                    # log data

                    kwargs['reviewer_name'] = request.reviewer_name

                    description = 'Reviewer {rev_name} un-assigned from registration request id: {req_id}'.format(
                        rev_name=kwargs['reviewer_name'], req_id=request.id)

                    log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="Registration Request",
                                                   request_details=request,
                                                   status=Status.get_status_type(request.status),
                                                   description=description)
                    EsLog.insert_log(log)

                    return Response(json.dumps(SuccessResponse().dump(res).data),
                                    status=201, mimetype='application/json')
                else:
                    res = {'error': ['invalid reviewer {id}'.format(id=reviewer_id)]}
                    return Response(json.dumps(ErrorResponse().dump(res).data),
                                    status=400, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')
        else:
            if DeRegDetails.exists(request_id):
                request = DeRegDetails.get_by_id(request_id)
                if request.reviewer_id == reviewer_id:
                    DeRegDetails.un_assign_request(request_id)
                    res = {
                        'message': 'Successfully un-assigned the request'
                    }

                    # log data
                    kwargs['reviewer_name'] = request.reviewer_name

                    description = 'Reviewer {rev_name} un-assigned from de-registration request id: {req_id}'.format(
                        rev_name=kwargs['reviewer_name'], req_id=request.id)

                    log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="De-Registration Request",
                                                   request_details=request,
                                                   status=Status.get_status_type(request.status),
                                                   description=description)
                    EsLog.insert_log(log)

                    return Response(json.dumps(SuccessResponse().dump(res).data),
                                    status=201, mimetype='application/json')
                else:
                    res = {'error': ['invalid reviewer {id}'.format(id=reviewer_id)]}
                    return Response(json.dumps(ErrorResponse().dump(res).data),
                                    status=400, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')


class ReviewSection(MethodResource):
    """Class for managing Section Review methods."""

    @doc(description='Review request sections', tags=['Reviewers'])
    @marshal_with(SuccessResponse, code=201, description='On success (section reviewed success)')
    @marshal_with(ErrorResponse, code=500, description='On Error')
    @marshal_with(ErrorResponse, code=422, description='On Error (Bad Arguments formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Request content not found)')
    @use_kwargs(SectionReviewArgs().fields_dict, locations=['json'])
    def put(self, **kwargs):
        """Handler for PUT method."""
        for key, value in kwargs.items():
            if value is None:
                res = {'error': ['{0} is required'.format(key)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=422, mimetype='application/json')

        review_section = kwargs.get('section')
        request_type = kwargs.get('request_type')
        section_status = kwargs.get('status')
        request_id = kwargs.get('request_id')
        comment = kwargs.get('comment')
        reviewer_id = kwargs.get('reviewer_id')
        reviewer_name = kwargs.get('reviewer_name')

        if section_status not in [5, 6, 7]:
            res = {
                'error': ['section_status must be Information Requested, Approved or Rejected']
            }

            return Response(json.dumps(ErrorResponse().dump(res).data),
                            status=422, mimetype='application/json')

        if request_type == RequestTypes.REG_REQUEST.value:
            if RegDetails.exists(request_id):
                request = RegDetails.get_by_id(request_id)
                if request.status == 4:
                    if request.reviewer_id == reviewer_id:
                        if request.report_status != 10:
                            res = {
                                'error': [_('request must be processed before reviewed.')]
                            }

                            return Response(app.json_encoder.encode(res),
                                            status=422, mimetype='application/json')

                        # log data
                        kwargs['section_status'] = Status.get_status_type(section_status)

                        description = 'Reviewer {rev_name} reviewed section {section}' \
                                      ' for registration request id: {req_id}'.\
                            format(rev_name=kwargs['reviewer_name'], req_id=request.id, section=review_section)

                        log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="Registration Request",
                                                       request_details=request,
                                                       status=Status.get_status_type(request.status),
                                                       description=description)
                        EsLog.insert_log(log)

                        RegDetails.add_comment(review_section,
                                               comment,
                                               reviewer_id,
                                               reviewer_name,
                                               section_status,
                                               request_id)
                    else:
                        res = {'error': ['invalid reviewer {id}'.format(id=reviewer_id)]}
                        return Response(json.dumps(ErrorResponse().dump(res).data),
                                        status=400, mimetype='application/json')
                else:
                    res = {'error': ['request {id} should be in-review'.format(id=request_id)]}
                    return Response(json.dumps(ErrorResponse().dump(res).data),
                                    status=400, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')
        else:
            if DeRegDetails.exists(request_id):
                request = DeRegDetails.get_by_id(request_id)
                if request.status == 4:
                    if request.reviewer_id == reviewer_id:
                        if request.report_status != 10:
                            res = {
                                'error': [_('request must be processed before reviewed.')]
                            }

                            return Response(app.json_encoder.encode(res),
                                            status=422, mimetype='application/json')
                        # log data
                        kwargs['section_status'] = Status.get_status_type(section_status)

                        description = 'Reviewer {rev_name} reviewed section {section}' \
                                      ' for de-registration request id: {req_id}'\
                            .format(rev_name=kwargs['reviewer_name'], req_id=request.id, section=review_section)

                        log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="De-Registration Request",
                                                       request_details=request,
                                                       status=Status.get_status_type(request.status),
                                                       description=description)
                        EsLog.insert_log(log)

                        DeRegDetails.add_comment(review_section,
                                                 comment,
                                                 reviewer_id,
                                                 reviewer_name,
                                                 section_status,
                                                 request_id)
                    else:
                        res = {'error': ['invalid reviewer {id}'.format(id=reviewer_id)]}
                        return Response(json.dumps(ErrorResponse().dump(res).data),
                                        status=400, mimetype='application/json')
                else:
                    res = {'error': ['request {id} should be in-review'.format(id=request_id)]}
                    return Response(json.dumps(ErrorResponse().dump(res).data),
                                    status=400, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')

        res = {
            'message': 'Comment on request added successfully'
        }

        return Response(json.dumps(SuccessResponse().dump(res).data),
                        status=201, mimetype='application/json')


class DeviceQuota(MethodResource):
    """Class for managing Device Quota Http Handlers."""

    @doc(description='Returns Device Quotas of a User', tags=['Reviewers'])
    @marshal_with(DeviceQuotaSchema, code=200, description='On success (Device quota of a user)')
    @marshal_with(ErrorResponse, code=500, description='On error (Un-identified Error)')
    @marshal_with(ErrorResponse, code=422, description='On error (Bad Argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Request content not found)')
    @use_kwargs(DeviceQuotaArgs().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """Handler for Device Quota GET Method."""
        request_id = kwargs.get('request_id')
        if request_id is None:  # if request_id is not present
            res = {'error': ['parameter request_id is required']}
            return Response(json.dumps(ErrorResponse().dump(res).data),
                            status=422, mimetype='application/json')

        allowed_import_quota = GLOBAL_CONF.get('importer')
        allowed_export_quota = GLOBAL_CONF.get('exporter')

        if RegDetails.exists(request_id):
            request = RegDetails.get_by_id(request_id)
            # get user device quota
            device_quota = DeviceQuotaModel.get(request.user_id)
            # get request device count
            device_count = request.device_count

            resp = {
                'allowed_import_quota': allowed_import_quota,
                'allowed_export_quota': allowed_export_quota,
                'used_registration_quota': allowed_import_quota - device_quota.reg_quota,
                'used_de_registration_quota': allowed_export_quota - device_quota.dreg_quota,
                'request_device_count': device_count
            }

            return Response(json.dumps(DeviceQuotaSchema().dump(resp).data),
                            status=200, mimetype='application/json')
        else:
            res = {'error': ['request {id} does not exists'.format(id=request_id)]}
            return Response(json.dumps(ErrorResponse().dump(res).data),
                            status=204, mimetype='application/json')


class DeviceDescription(MethodResource):
    """Class for handling Device Description methods."""

    @doc(description='Returns device description related to a request', tags=['Reviewers'])
    @marshal_with(DevicesDescription, code=200, description='On success')
    @marshal_with(ErrorResponse, code=500, description='On Error (Un-identified error)')
    @marshal_with(ErrorResponse, code=422, description='On Error (Bad Argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Request content not found)')
    @use_kwargs(DeviceDescriptionArgs().fields_dict, locations=['query'])
    def get(self, **kwargs):  # pylint: disable=too-many-statements
        """GET method handler for Devices Descriptions of a Request."""
        request_id = kwargs.get('request_id')
        request_type = kwargs.get('request_type')
        # if it is a registration type request
        if request_type == RequestTypes.REG_REQUEST.value:
            if RegDetails.exists(request_id):
                request = RegDetails.get_by_id(request_id)
                devices = request.devices
                device_imeis = []
                for device in devices:
                    device_imeis.append(device.imeis)
                normalized_imeis = []
                for imei in device_imeis:
                    normalized_imeis.append(imei[0].normalized_imei)

                tacs = self.extract_tacs(normalized_imeis)
                app.logger.info('tacs for device description: {0}'.format(tacs))
                gsma_device_descp = Utilities.get_devices_description(tacs)

                device = RegDevice.get_by_id(request.devices[0].reg_device_id)
                device_type = DeviceType.get_device_type_by_id(device.device_types_id)

                technologies = []
                for tech in device.device_technologies:
                    tec_id = tech.technology_id
                    technology = Technologies.get_technology_by_id(tec_id)
                    technologies.append(technology)

                user_device_descp = [{
                    'brand': device.brand,
                    'model_name': device.model_name,
                    'model_number': device.model_num,
                    'operating_system': device.operating_system,
                    'device_type': device_type,
                    'radio_access_technology': ','.join(str(tech) for tech in technologies)
                }]

                response = {
                    'user_device_description': user_device_descp
                }

                if len(tacs) > 1:
                    if gsma_device_descp.get('results') is not None:
                        gsma = []
                        for gsma_descp in gsma_device_descp.get('results'):
                            gsma.append(gsma_descp.get('gsma'))
                        response['gsma_device_description'] = gsma
                    else:
                        gsma = []
                        for tac in tacs:  # pylint: disable=unused-variable
                            gsma.append(None)
                        response['gsma_device_description'] = gsma
                else:
                    if gsma_device_descp.get('gsma') is not None:
                        response['gsma_device_description'] = gsma_device_descp.get('gsma')
                    else:
                        response['gsma_device_description'] = [None]

                return Response(json.dumps(DevicesDescription().dump(response).data),
                                status=200, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')
        else:  # if it is de-registration type request
            if DeRegDetails.exists(request_id):
                request = DeRegDetails.get_by_id(request_id)
                devices = request.devices
                tacs = [device.tac for device in devices]
                gsma_device_descp = Utilities.get_devices_description(tacs)

                user_devices_descp = []
                for device in devices:
                    user_device = DeRegDevice.get_by_id(device.id)
                    device_descp = {
                        'brand': user_device.brand,
                        'model_name': user_device.model_name,
                        'model_number': user_device.model_num,
                        'operating_system': user_device.operating_system,
                        'device_type': user_device.device_type,
                        'radio_access_technology': user_device.technology
                    }
                    user_devices_descp.append(device_descp)

                response = {
                    'user_device_description': user_devices_descp
                }
                if len(tacs) > 1:
                    if gsma_device_descp.get('results') is not None:
                        gsma = []
                        for gsma_descp in gsma_device_descp.get('results'):
                            gsma.append(gsma_descp.get('gsma'))
                        response['gsma_device_description'] = gsma
                    else:
                        gsma = [None for tac in tacs]
                        response['gsma_device_description'] = gsma
                else:
                    if gsma_device_descp.get('gsma') is not None:
                        response['gsma_device_description'] = gsma_device_descp.get('gsma')
                    else:
                        response['gsma_device_description'] = [None]

                return Response(json.dumps(DevicesDescription().dump(response).data),
                                status=200, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')


    # noinspection PyMethodMayBeStatic
    def extract_tacs(self, imeis):
        """Method to extract unique tacs from imeis."""
        tacs = [imei[:8] for imei in imeis]
        tacs = set(tacs)
        return list(tacs)


class IMEIRegistrationStatus(MethodResource):
    """Class for handling IMEI-Registration status."""

    @doc(description='Shows Registration status of the IMEIs of user request', tags=['Reviewers'])
    @marshal_with(IMEIRegStatus, code=200, description='On success')
    @marshal_with(ErrorResponse, code=500, description='On Error (Un-identified Error)')
    @marshal_with(ErrorResponse, code=422, description='On Error (Bad Argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Request content not found)')
    @use_kwargs(IMEIRegStatusArgs().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """GET method handler for IMEI Registration status of a user."""
        request_id = kwargs.get('request_id')
        request_type = kwargs.get('request_type')

        if request_id is None:
            res = {'error': ['request_id is required']}
            return Response(json.dumps(ErrorResponse().dump(res).data),
                            status=422, mimetype='application/json')

        if request_type is None:
            res = {'error': ['request_type is required']}
            return Response(json.dumps(ErrorResponse().dump(res).data),
                            status=422, mimetype='application/json')

        if request_type == RequestTypes.REG_REQUEST.value:
            if RegDetails.exists(request_id):
                request = RegDetails.get_by_id(request_id)
                res = RegDetails.get_imeis_count(request.user_id)

                # calc duplicated imeis
                duplicated_imeis = RegDetails.get_duplicate_imeis(request)
                if duplicated_imeis and not request.status == 6:
                    res.update({'duplicated': len(RegDetails.get_duplicate_imeis(request))})
                    Utilities.generate_imeis_file(duplicated_imeis, request.tracking_id, 'duplicated_imeis')
                    request.duplicate_imeis_file = '{upload_dir}/{tracking_id}/{file}'.format(
                        upload_dir=app.config['DRS_UPLOADS'],
                        tracking_id=request.tracking_id,
                        file='duplicated_imeis.txt'
                    )
                RegDetails.commit_case_changes(request)
                return Response(json.dumps(IMEIRegStatus().dump(res).data), status=200, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')
        # return for de-reg request
        else:
            if DeRegDetails.exists(request_id):
                request = DeRegDetails.get_by_id(request_id)
                res = DeRegDetails.get_imeis_count(request.user_id)
                imeis = DeRegDetails.get_normalized_imeis(request)
                invalid_imeis = Utilities.get_not_registered_imeis(imeis)  # return only invalid imeis
                res.update({'invalid': len(invalid_imeis)})

                # generate invalid imei file
                if invalid_imeis:
                    Utilities.generate_imeis_file(invalid_imeis, request.tracking_id, 'invalid_imeis')
                    request.invalid_imeis_file = '{upload_dir}/{tracking_id}/{file}'.format(
                        upload_dir=GLOBAL_CONF.get('upload_directory'),
                        tracking_id=request.tracking_id,
                        file='invalid_imeis.txt'
                    )
                DeRegDetails.commit_case_changes(request)
                return Response(json.dumps(IMEIRegStatus().dump(res).data), status=200, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')


class RequestDocuments(MethodResource):
    """Class for handling Request documents API"""

    @doc(description='Generate and return request documents links', tags=['Reviewers'])
    @marshal_with(Documents, code=200, description='On success')
    @marshal_with(ErrorResponse, code=500, description='On error (Un-identified error)')
    @marshal_with(ErrorResponse, code=422, description='On error (Bad Argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Request content not found)')
    @use_kwargs(DocumentsApiArgs().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """GET method handler for Request documents."""
        request_id = kwargs.get('request_id')
        request_type = kwargs.get('request_type')

        if request_id is None:
            res = {'error': ['request_id is required']}
            return Response(json.dumps(ErrorResponse().dump(res).data),
                            status=422, mimetype='application/json')

        if request_type is None:
            res = {'error': ['request_type is required']}
            return Response(json.dumps(ErrorResponse().dump(res).data),
                            status=422, mimetype='application/json')

        if request_type == RequestTypes.REG_REQUEST.value:
            if RegDetails.exists(request_id):
                request = RegDetails.get_by_id(request_id)
                tracking_id = request.tracking_id
                docs = []
                for document in request.documents:
                    reg_doc = ReqDocument.get_document_by_id(document.document_id)
                    dat = {
                        'document_type': reg_doc.label,
                        'link': '{server_dir}/{local_dir}/{file_name}'.format(
                            server_dir=app.config['DRS_UPLOADS'],
                            local_dir=tracking_id,
                            file_name=document.filename
                        )
                    }
                    docs.append(dat)
                return Response(json.dumps(Documents().dump({'documents': docs}).data), status=200,
                                mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')
        else:
            if DeRegDetails.exists(request_id):
                request = DeRegDetails.get_by_id(request_id)
                tracking_id = request.tracking_id
                docs = []
                for document in request.documents:
                    dreg_doc = ReqDocument.get_document_by_id(document.document_id)
                    dat = {
                        'document_type': dreg_doc.label,
                        'link': '{server_dir}/{local_dir}/{file_name}'.format(
                            server_dir=app.config['DRS_UPLOADS'],
                            local_dir=tracking_id,
                            file_name=document.filename
                        )
                    }
                    docs.append(dat)
                return Response(json.dumps(Documents().dump({'documents': docs}).data), status=200,
                                mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')


class Sections(MethodResource):
    """Class for handling routes related to request sections."""

    @doc(description='Get all sections information of a request', tags=['Reviewers'])
    @marshal_with(SectionSchema, code=200, description='On success')
    @marshal_with(ErrorResponse, code=500, description='On Error (Un-identified error)')
    @marshal_with(ErrorResponse, code=422, description='On Error (Bad Argument formats)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Request content not found)')
    @use_kwargs(SectionsArgs().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """GET method handler for sections route."""
        for key, value in kwargs.items():
            if value is None:
                res = {'error': ['{0} is required'.format(key)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=422, mimetype='application/json')

        request_id = kwargs.get('request_id')
        request_type = kwargs.get('request_type')

        # if registration request
        if request_type == RequestTypes.REG_REQUEST.value:
            if RegDetails.exists(request_id):
                response = []
                for section in SectionTypes:
                    sec = RegDetails.get_section_by_state(request_id, section.value)
                    response.append(sec)
                return Response(json.dumps(SectionSchema().dump(dict({'sections': response})).data),
                                status=200, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')

        else:  # de-registration request
            if DeRegDetails.exists(request_id):
                response = []
                for section in SectionTypes:
                    if section.value != SectionTypes.DEVICE_QUOTA.value:
                        sec = DeRegDetails.get_section_by_state(request_id, section.value)
                        response.append(sec)
                return Response(json.dumps(SectionSchema().dump(dict({'sections': response})).data),
                                status=200, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')


# noinspection PyMethodMayBeStatic
class SubmitReview(MethodResource):
    """Class for handling complete Review Submission routes."""

    def __generate_notification(self, user_id, request_id, request_type, request_status, message):
        """Private method to generate notification on application successful review submission."""
        try:
            notification = Notification(user_id, request_id, request_type, request_status, message)
            notification.add()
            return True
        except SQLAlchemyError as e:
            app.logger.error('Unable to generate notification for this request, see logs below')
            app.logger.exception(e)
            return False

    def __update_to_approved_imeis(self, imeis):
        """Method to update pending imeis to approved in the table"""
        imei_status = 'whitelist'
        imei_delta_status = 'update'
        updated_imeis = []

        for imei in imeis:
            if ApprovedImeis.exists(imei):
                imei_ = ApprovedImeis.get_imei(imei)
                imei_.status = imei_status

                # fix: DDRS-286
                # if an imei was in pending and exported to core then update the status
                # else keep the delta status as add because if an imei was not exported at
                # first and is now going in the list then core import will throw an error
                # of not existence
                if imei_.exported:
                    imei_.delta_status = imei_delta_status
                    updated_imeis.append(imei_)
        ApprovedImeis.bulk_insert_imeis(updated_imeis)

    def __change_rejected_imeis_status(self, imeis):
        """Method to change the status of imeis which are provisionally registered."""
        changed_imeis = []
        time_now = datetime.datetime.now()
        for imei in imeis:
            provisional_imei = ApprovedImeis.get_imei(imei)
            if (provisional_imei.status == 'pending' or not provisional_imei.status == 'removed') and (
                    provisional_imei.exported_at is None or time_now > provisional_imei.exported_at):
                if provisional_imei.status != 'whitelist':
                    if provisional_imei.exported:
                        provisional_imei.delta_status = 'remove'
                        provisional_imei.status = 'removed'
                        changed_imeis.append(provisional_imei)
                    else:
                        provisional_imei.delta_status = 'remove'
                        provisional_imei.status = 'removed'
                        provisional_imei.removed = True
                        changed_imeis.append(provisional_imei)

        ApprovedImeis.bulk_insert_imeis(changed_imeis)

    @doc(description='Submit a request after final review', tags=['Reviewers'])
    @marshal_with(SubmitSuccessResponse, code=201, description='On success (Case status updated)')
    @marshal_with(ErrorResponse, code=422, description='On Error (Bad Argument formats)')
    @marshal_with(ErrorResponse, code=400, description='On Error (Bad Request)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Request content not found)')
    @marshal_with(ErrorResponse, code=500, description='On Error (Un-identified error)')
    @use_kwargs(SubmitReviewArgs().fields_dict, locations=['json'])
    # pylint: disable=too-many-statements
    def put(self, **kwargs):
        """PUT method handler."""
        for key, value in kwargs.items():
            if value is None:
                res = {'error': ['{0} is required'.format(key)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=422, mimetype='application/json')

        request_id = kwargs.get('request_id')
        request_type = kwargs.get('request_type')
        reviewer_id = kwargs.get('reviewer_id')

        if request_type == RequestTypes.REG_REQUEST.value:  # registration request
            if RegDetails.exists(request_id):
                request = RegDetails.get_by_id(request_id)
                # if request is approved, rejected or closed, do nothing
                if request.status in [f.value for f in RequestStatusTypes]:
                    res = {
                        'error': ['Request cannot be entertained, request is already {0}'.format(
                            RequestStatusTypes(request.status).name)]
                    }
                    return Response(json.dumps(ErrorResponse().dump(res).data),
                                    status=400, mimetype='application/json')
                else:
                    if request.reviewer_id == reviewer_id:
                        sections_info = []
                        for section in SectionTypes:
                            sec = RegDetails.get_section_by_state(request_id, section.value)
                            sections_info.append(sec.get('section_status'))

                        # check if any section is rejected
                        if any(status == 7 for status in sections_info):
                            case_status = 7
                            request.status = case_status
                            RegDetails.commit_case_changes(request)

                            # change imei status
                            imeis = RegDetails.get_normalized_imeis(request)
                            self.__change_rejected_imeis_status(imeis)

                            # generate notification
                            message = 'Your request {id} has been rejected'.format(id=request.id)
                            self.__generate_notification(user_id=request.user_id, request_id=request_id,
                                                         request_type=request_type, request_status=case_status,
                                                         message=message)

                            res = {
                                'request_id': request_id,
                                'request_type': request_type,
                                'status': request.status,
                                'message': 'case {id} updated successfully'.format(id=request_id)
                            }

                            # log data
                            request = RegDetails.get_by_id(request_id)
                            kwargs['reviewer_name'] = request.reviewer_name
                            description = 'Reviewer {rev_name} rejected registration request id: ' \
                                          '{req_id} because sections are in rejected state'\
                                .format(rev_name=kwargs['reviewer_name'], req_id=request.id)

                            log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="Registration Request",
                                                           request_details=request,
                                                           status=Status.get_status_type(request.status),
                                                           description=description)
                            EsLog.insert_log(log)

                            return Response(json.dumps(SubmitSuccessResponse().dump(res).data),
                                            status=201, mimetype='application/json')
                        elif all(status == 6 for status in sections_info):
                            case_status = 6

                            # check if imeis are already duplicated than don't approve
                            duplicated_imeis = RegDetails.get_duplicate_imeis(request)
                            if duplicated_imeis:
                                res = {'error': [
                                    _('unable to approve case %(id)s, duplicated imeis found', id=request_id)
                                ]}
                                return Response(app.json_encoder.encode(res),
                                                status=400, mimetype='application/json')

                            # else if not duplicated continue
                            request.status = case_status
                            RegDetails.commit_case_changes(request)

                            # checkout device quota
                            imeis = RegDetails.get_normalized_imeis(request)
                            user_quota = DeviceQuotaModel.get(request.user_id)
                            current_quota = user_quota.reg_quota
                            user_quota.reg_quota = current_quota - len(imeis)
                            DeviceQuotaModel.commit_quota_changes(user_quota)

                            # add imeis to approved imeis table
                            self.__update_to_approved_imeis(imeis)

                            # generate notification
                            message = 'Your request {id} has been approved'.format(id=request.id)
                            self.__generate_notification(user_id=request.user_id, request_id=request_id,
                                                         request_type=request_type, request_status=case_status,
                                                         message=message)

                            res = {
                                'request_id': request_id,
                                'request_type': request_type,
                                'status': request.status,
                                'message': 'case {id} updated successfully'.format(id=request_id)
                            }

                            # log data
                            request = RegDetails.get_by_id(request_id)
                            kwargs['reviewer_name'] = request.reviewer_name
                            description = 'Reviewer {rev_name} approved registration request id: {req_id}' \
                                .format(rev_name=kwargs['reviewer_name'], req_id=request.id)

                            log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="Registration Request",
                                                           request_details=request,
                                                           status=Status.get_status_type(request.status),
                                                           description=description)
                            EsLog.insert_log(log)

                            return Response(json.dumps(SubmitSuccessResponse().dump(res).data),
                                            status=201, mimetype='application/json')
                        # check if any section is information requested state
                        elif any(status == 5 for status in sections_info):
                            case_status = 5
                            request.status = case_status
                            RegDetails.commit_case_changes(request)

                            # generate notification
                            message = 'Your request {id} has been reviewed'.format(id=request.id)
                            self.__generate_notification(user_id=request.user_id, request_id=request_id,
                                                         request_type=request_type, request_status=case_status,
                                                         message=message)

                            res = {
                                'request_id': request_id,
                                'request_type': request_type,
                                'status': request.status,
                                'message': 'case {id} updated successfully'.format(id=request_id)
                            }

                            # log data
                            request = RegDetails.get_by_id(request_id)
                            kwargs['reviewer_name'] = request.reviewer_name
                            description = 'Reviewer {rev_name} reviewed registration request id: {req_id}' \
                                .format(rev_name=kwargs['reviewer_name'], req_id=request.id)

                            log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="Registration Request",
                                                           request_details=request,
                                                           status=Status.get_status_type(request.status),
                                                           description=description)
                            EsLog.insert_log(log)

                            return Response(json.dumps(SubmitSuccessResponse().dump(res).data),
                                            status=201, mimetype='application/json')
                        elif any(status is None for status in sections_info):
                            res = {'error': [
                                'unable to update case {id}, complete review process'.format(id=request_id)
                            ]}
                            return Response(json.dumps(ErrorResponse().dump(res).data),
                                            status=400, mimetype='application/json')
                        else:
                            res = {'error': [
                                'unable to update case {id}, complete review process'.format(id=request_id)
                            ]}
                            return Response(json.dumps(ErrorResponse().dump(res).data),
                                            status=400, mimetype='application/json')
                    else:
                        res = {'error': ['invalid reviewer {id}'.format(id=reviewer_id)]}
                        return Response(json.dumps(ErrorResponse().dump(res).data),
                                        status=400, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')

        else:  # de-registration request
            if DeRegDetails.exists(request_id):
                request = DeRegDetails.get_by_id(request_id)
                # if request is approved, rejected or closed, do nothing
                if request.status in [f.value for f in RequestStatusTypes]:
                    res = {
                        'error': ['Request cannot be entertained, request is already {0}'.format(
                            RequestStatusTypes(request.status).name)]
                    }
                    return Response(json.dumps(ErrorResponse().dump(res).data),
                                    status=400, mimetype='application/json')
                else:
                    if request.reviewer_id == reviewer_id:
                        sections_info = []
                        for section in SectionTypes:
                            if not section.value == SectionTypes.DEVICE_QUOTA.value:
                                # skip device quota
                                sec = DeRegDetails.get_section_by_state(request_id, section.value)
                                sections_info.append(sec.get('section_status'))

                        # check if any section is rejected
                        if any(status == 7 for status in sections_info):
                            case_status = 7
                            request.status = case_status
                            DeRegDetails.commit_case_changes(request)

                            # generate notification
                            message = 'Your request {id} has been rejected'.format(id=request.id)
                            self.__generate_notification(user_id=request.user_id, request_id=request_id,
                                                         request_type=request_type, request_status=case_status,
                                                         message=message)

                            res = {
                                'request_id': request_id,
                                'request_type': request_type,
                                'status': request.status,
                                'message': 'case {id} updated successfully'.format(id=request_id)
                            }

                            # log data
                            kwargs['reviewer_name'] = request.reviewer_name
                            description = 'Reviewer {rev_name} rejected de-registration request id: ' \
                                          '{req_id} because the sections are in rejected state' \
                                .format(rev_name=kwargs['reviewer_name'], req_id=request.id)

                            log = EsLog.reviewer_serialize(kwargs, method='Put', review_type="De-Registration Request",
                                                           request_details=request,
                                                           status=Status.get_status_type(request.status),
                                                           description=description)
                            EsLog.insert_log(log)

                            return Response(json.dumps(SubmitSuccessResponse().dump(res).data),
                                            status=201, mimetype='application/json')
                        elif all(status == 6 for status in sections_info):
                            case_status = 6
                            imeis = DeRegDetails.get_normalized_imeis(request)
                            return_status = Utilities.de_register_imeis(imeis)
                            invalid_imeis = Utilities.get_not_registered_imeis(imeis)
                            if return_status:
                                request.status = case_status
                                DeRegDetails.commit_case_changes(request)

                                # generate notification
                                message = 'Your request {id} has been approved'.format(id=request.id)
                                self.__generate_notification(user_id=request.user_id, request_id=request_id,
                                                             request_type=request_type, request_status=case_status,
                                                             message=message)

                                res = {
                                    'request_id': request_id,
                                    'request_type': request_type,
                                    'status': request.status,
                                    'message': 'case {id} updated successfully'.format(id=request_id)
                                }

                                # log data
                                kwargs['reviewer_name'] = request.reviewer_name
                                description = 'Reviewer {rev_name} approved de-registration request id: {req_id}'\
                                    .format(rev_name=kwargs['reviewer_name'], req_id=request.id)

                                log = EsLog.reviewer_serialize(kwargs, method='Put',
                                                               review_type="De-Registration Request",
                                                               request_details=request,
                                                               status=Status.get_status_type(request.status),
                                                               description=description)
                                EsLog.insert_log(log)

                                return Response(json.dumps(SubmitSuccessResponse().dump(res).data),
                                                status=201, mimetype='application/json')
                            elif return_status is False and invalid_imeis:
                                res = {
                                    'error': _('Unable to approve, invalid imeis found')
                                }
                                return Response(json.dumps(ErrorResponse().dump(res).data),
                                                status=400, mimetype='application/json')
                            else:
                                res = {
                                    'error': 'Unable to De-Register IMEIs, check system logs'
                                }
                                return Response(json.dumps(ErrorResponse().dump(res).data),
                                                status=500, mimetype='application/json')

                        # check if any section is information requested state
                        elif any(status == 5 for status in sections_info):
                            case_status = 5
                            request.status = case_status
                            DeRegDetails.commit_case_changes(request)

                            # generate notification
                            message = 'Your request {id} has been reviewed'.format(id=request.id)
                            self.__generate_notification(user_id=request.user_id, request_id=request_id,
                                                         request_type=request_type, request_status=case_status,
                                                         message=message)

                            res = {
                                'request_id': request_id,
                                'request_type': request_type,
                                'status': request.status,
                                'message': 'case {id} updated successfully'.format(id=request_id)
                            }

                            # log data
                            kwargs['reviewer_name'] = request.reviewer_name
                            description = 'Reviewer {rev_name} reviewed de-registration request id: {req_id}' \
                                .format(rev_name=kwargs['reviewer_name'], req_id=request.id)

                            log = EsLog.reviewer_serialize(kwargs, method='Put',
                                                           review_type="De-Registration Request",
                                                           request_details=request,
                                                           status=Status.get_status_type(request.status),
                                                           description=description)
                            EsLog.insert_log(log)

                            return Response(json.dumps(SubmitSuccessResponse().dump(res).data),
                                            status=201, mimetype='application/json')
                        elif any(status is None for status in sections_info):
                            res = {'error': [
                                'unable to update case {id}, complete the review process'.format(id=request_id)]}
                            return Response(json.dumps(ErrorResponse().dump(res).data),
                                            status=400, mimetype='application/json')
                        else:
                            res = {'error': [
                                'unable to update case {id}, complete the review process'.format(id=request_id)]}
                            return Response(json.dumps(ErrorResponse().dump(res).data),
                                            status=400, mimetype='application/json')
                    else:
                        res = {'error': ['invalid reviewer {id}'.format(id=reviewer_id)]}
                        return Response(json.dumps(ErrorResponse().dump(res).data),
                                        status=400, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')


class IMEIClassification(MethodResource):
    """Class for handling IMEI Classifications Route."""

    @doc(description='Returns Classification states of IMEIs of current request', tags=['Reviewers'])
    @marshal_with(IMEIClassificationSchema, code=200, description='On success')
    @marshal_with(ErrorResponse, code=422, description='On Error (Bad Argument formats)')
    @marshal_with(ErrorResponse, code=500, description='On Error (Un-identified error)')
    @marshal_with(ErrorResponse, code=204, description='On Error (Requested content does not exist)')
    @use_kwargs(SectionsArgs().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """GET method handler"""
        request_id = kwargs.get('request_id')
        request_type = kwargs.get('request_type')

        if request_id is None:
            res = {'error': ['request_id is required']}
            return Response(json.dumps(ErrorResponse().dump(res).data),
                            status=422, mimetype='application/json')

        if request_type is None:
            res = {'error': ['request_type is required']}
            return Response(json.dumps(ErrorResponse().dump(res).data),
                            status=422, mimetype='application/json')

        if request_type == RequestTypes.REG_REQUEST.value:
            if RegDetails.exists(request_id):
                request = RegDetails.get_by_id(request_id)
                if request.summary is not None:
                    summary = json.loads(request.summary).get('summary')
                    res = {
                        'imei_compliance_status': {
                            'compliant_imeis': summary.get('complaint'),
                            'non_compliant_imeis': summary.get('non_complaint'),
                            'provisional_compliant': summary.get('provisional_compliant'),
                            'provisional_non_compliant': summary.get('provisional_non_compliant')
                        },
                        'per_condition_classification_state': {
                            key: value for key, value in summary.get('count_per_condition').items()
                        },
                        'lost_stolen_status': {
                            'provisional_stolen': summary.get('provisional_stolen'),
                            'stolen': summary.get('stolen')
                        },
                        'seen_on_network': summary.get('seen_on_network')
                    }
                    return Response(json.dumps(IMEIClassificationSchema().dump(res).data),
                                    status=200, mimetype='application/json')
                else:
                    res = {}
                    return Response(json.dumps(res), status=200, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')
        else:
            if DeRegDetails.exists(request_id):
                request = DeRegDetails.get_by_id(request_id)
                imeis = DeRegDetails.get_normalized_imeis(request)
                count = ImeiAssociation.bulk_exists(imeis)
                if request.summary is not None:
                    summary = json.loads(request.summary).get('summary')
                    res = {
                        'imei_compliance_status': {
                            'compliant_imeis': summary.get('complaint'),
                            'non_compliant_imeis': summary.get('non_complaint'),
                            'provisional_compliant': summary.get('provisional_compliant'),
                            'provisional_non_compliant': summary.get('provisional_non_compliant')
                        },
                        'per_condition_classification_state': {
                            key: value for key, value in summary.get('count_per_condition').items()
                        },
                        'lost_stolen_status': {
                            'provisional_stolen': summary.get('provisional_stolen'),
                            'stolen': summary.get('stolen')
                        },
                        'seen_on_network': summary.get('seen_on_network'),
                        'associated_imeis': count
                    }
                    return Response(json.dumps(IMEIClassificationSchema().dump(res).data),
                                    status=200, mimetype='application/json')
                else:
                    res = {'error': ['request {id} summary not generated yet'.format(id=request_id)]}
                    return Response(json.dumps(res), status=200, mimetype='application/json')
            else:
                res = {'error': ['request {id} does not exists'.format(id=request_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data),
                                status=204, mimetype='application/json')
