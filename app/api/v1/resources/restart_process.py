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

from flask import Response
from flask_restful import Resource
from marshmallow import ValidationError
from flask_babel import gettext as _

from app import app, db
from app.api.v1.helpers.error_handlers import REG_NOT_FOUND_MSG, DEREG_NOT_FOUND_MSG
from app.api.v1.helpers.response import MIME_TYPES, CODES
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.models.deregdetails import DeRegDetails
from app.api.v1.models.deregdevice import DeRegDevice
from app.api.v1.models.device import Device
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.regdevice import RegDevice
from app.api.v1.models.status import Status
from app.api.v1.schema.deregdevice import DeRegDeviceSchema


class RegistrationProcessRestart(Resource):
    """Class for handling process routes."""
    @staticmethod
    def post(reg_id):
        """POST method handler, restarts processing of a request."""
        if not reg_id or not reg_id.isdigit() or not RegDetails.exists(reg_id):
            return Response(app.json_encoder.encode(REG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        try:
            reg_details = RegDetails.get_by_id(reg_id)
            # day_passed = (datetime.now() - reg_details.updated_at) > timedelta(1)
            failed_status_id = Status.get_status_id('Failed')
            processing_failed = reg_details.processing_status in [failed_status_id]
            report_failed = reg_details.report_status in [failed_status_id]
            # report_timeout = reg_details.report_status == Status.get_status_id('Processing') and day_passed
            processing_required = processing_failed or report_failed

            if processing_required:  # pragma: no cover
                reg_device = RegDevice.get_device_by_registration_id(reg_details.id)
                Device.create(reg_details, reg_device.id)
                response = {'message': 'Request performed successfully.'}
            else:
                response = app.json_encoder.encode({'message': _('This request cannot be processed')})

            return Response(json.dumps(response), status=CODES.get("OK"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        except Exception as e:  # pragma: no cover
            db.session.rollback()
            app.logger.exception(e)

            data = {
                'message': _('failed to restart process')
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))


class DeRegistrationProcessRestart(Resource):
    """Class for handling processing routes for De-Registration."""
    @staticmethod
    def post(dereg_id):
        """POST method handler, restarts processing of a request."""
        if not dereg_id or not dereg_id.isdigit() or not DeRegDetails.exists(dereg_id):
            return Response(app.json_encoder.encode(DEREG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        try:
            dereg = DeRegDetails.get_by_id(dereg_id)
            # day_passed = (datetime.now() - dereg.updated_at) > timedelta(1)
            failed_status_id = Status.get_status_id('Failed')
            processing_failed = dereg.processing_status in [failed_status_id]
            report_failed = dereg.report_status in [failed_status_id]
            # report_timeout = dereg.report_status == Status.get_status_id('Processing') and day_passed
            processing_required = processing_failed or report_failed
            if processing_required:  # pragma: no cover
                dereg_devices = DeRegDevice.get_devices_by_dereg_id(dereg.id)
                dereg_devices_data = DeRegDeviceSchema().dump(dereg_devices, many=True).data
                dereg_devices_ids = list(map(lambda x: x['id'], dereg_devices_data))
                args = {'devices': dereg_devices_data}
                imei_tac_map = Utilities.extract_imeis_tac_map(args, dereg)
                imeis_list = Utilities.extract_imeis(imei_tac_map)
                created = DeRegDevice.bulk_create(args, dereg)
                device_id_tac_map = Utilities.get_id_tac_map(created)
                DeRegDevice.bulk_insert_imeis(device_id_tac_map, imei_tac_map, dereg_devices_ids, imeis_list, dereg)
                response = {'message': 'Request performed successfully.'}
            else:
                response = app.json_encoder.encode({'message': _('This request cannot be processed')})

            return Response(json.dumps(response), status=CODES.get("OK"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            db.session.rollback()
            app.logger.exception(e)

            data = {
                'message': _('failed to restart process')
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
