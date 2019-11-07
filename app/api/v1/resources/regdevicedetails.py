"""
DRS Registration device resource package.
Copyright (c) 2018-2019 Qualcomm Technologies, Inc.
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

from flask import Response, request
from flask_restful import Resource
from marshmallow import ValidationError
from flask_babel import lazy_gettext as _

from app import app, db
from app.api.v1.helpers.error_handlers import REG_NOT_FOUND_MSG
from app.api.v1.helpers.response import MIME_TYPES, CODES
from app.api.v1.models.device import Device
from app.api.v1.models.devicetechnology import DeviceTechnology
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.regdevice import RegDevice
from app.api.v1.models.status import Status
from app.api.v1.schema.devicedetails import DeviceDetailsSchema
from app.api.v1.schema.devicedetailsupdate import DeviceDetailsUpdateSchema


class DeviceDetailsRoutes(Resource):
    """Class for handling Device Details routes."""

    @staticmethod
    def get(reg_id):
        """GET method handler, returns device details."""
        if not reg_id.isdigit() or not RegDetails.exists(reg_id):
            return Response(app.json_encoder.encode(REG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        schema = DeviceDetailsSchema()
        try:
            reg_device = RegDevice.get_device_by_registration_id(reg_id)
            response = schema.dump(reg_device).data if reg_device else {}
            return Response(json.dumps(response), status=CODES.get("OK"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            app.logger.exception(e)
            error = {
                'message': [_('Failed to retrieve response, please try later')]
            }
            return Response(app.json_encoder.encode(error), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()

    @staticmethod
    def post():
        """POST method handler, creates a new device."""
        reg_id = request.form.to_dict().get('reg_id', None)
        if not reg_id or not reg_id.isdigit() or not RegDetails.exists(reg_id):
            return Response(app.json_encoder.encode(REG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        try:
            args = request.form.to_dict()
            schema = DeviceDetailsSchema()
            reg_details = RegDetails.get_by_id(reg_id)
            if reg_details:
                args.update({'reg_details_id': reg_details.id})
            else:
                args.update({'reg_details_id': ''})

            validation_errors = schema.validate(args)
            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            reg_device = RegDevice.create(args)
            reg_device.technologies = DeviceTechnology.create(reg_device.id, args.get('technologies'))
            response = schema.dump(reg_device, many=False).data
            response['reg_details_id'] = reg_details.id
            reg_details.update_status('Awaiting Documents')
            db.session.commit()
            Device.create(reg_details, reg_device.id)
            return Response(json.dumps(response), status=CODES.get("OK"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        except Exception as e:  # pragma: no cover
            db.session.rollback()
            app.logger.exception(e)

            data = {
                'message': _('request device addition failed')
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()

    @staticmethod
    def put():
        """PUT method handler, updates a device."""
        reg_id = request.form.to_dict().get('reg_id', None)
        if not reg_id or not reg_id.isdigit() or not RegDetails.exists(reg_id):
            return Response(app.json_encoder.encode(REG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        try:
            args = request.form.to_dict()
            schema = DeviceDetailsUpdateSchema()
            reg_details = RegDetails.get_by_id(reg_id)
            reg_device = RegDevice.get_device_by_registration_id(reg_id)

            if reg_details:
                args.update({'reg_details_id': reg_details.id, 'status': reg_details.status})
            else:
                args.update({'reg_details_id': ''})
            validation_errors = schema.validate(args)
            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            # day_passed = (datetime.now() - reg_details.updated_at) > timedelta(1)
            processing_failed = reg_details.processing_status in [Status.get_status_id('Failed'),
                                                             Status.get_status_id('New Request')]
            report_failed = reg_details.report_status == Status.get_status_id('Failed')
            # report_timeout = reg_details.report_status == Status.get_status_id('Processing') and day_passed
            processing_required = processing_failed or report_failed

            reg_device = RegDevice.update(reg_device, args)
            response = schema.dump(reg_device, many=False).data
            response['reg_details_id'] = reg_details.id
            if processing_required:
                Device.create(reg_details, reg_device.id)

            return Response(json.dumps(response), status=CODES.get("OK"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        except Exception as e:  # pragma: no cover
            db.session.rollback()
            app.logger.exception(e)

            data = {
                'message': _('request device addition failed')
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))

        finally:
            db.session.close()
