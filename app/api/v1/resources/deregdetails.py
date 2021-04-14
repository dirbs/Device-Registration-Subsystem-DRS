"""
DRS De-Registration resource package.
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.
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
import uuid

from flask import Response, request
from flask_restful import Resource
from flask_babel import lazy_gettext as _
from marshmallow import ValidationError

from app import app, db
from app.api.v1.helpers.error_handlers import DEREG_NOT_FOUND_MSG
from app.api.v1.helpers.response import MIME_TYPES, CODES
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.models.deregdetails import DeRegDetails
from app.api.v1.models.deregdevice import DeRegDevice
from app.api.v1.models.deregdocuments import DeRegDocuments
from app.api.v1.models.status import Status
from app.api.v1.schema.deregdetails import DeRegDetailsSchema
from app.api.v1.schema.deregdetailsupdate import DeRegDetailsUpdateSchema
from app.api.v1.schema.deregdevice import DeRegDeviceSchema
from app.api.v1.schema.deregdocuments import DeRegDocumentsSchema
from app.api.v1.models.eslog import EsLog


class DeRegistrationRoutes(Resource):
    """Class for handling De-Registration Request Routes."""

    @staticmethod
    def get(dereg_id=None):
        """GET method handler,
        returns a deregistration request based on request id.
        """
        schema = DeRegDetailsSchema()
        try:
            if dereg_id:
                if dereg_id.isdigit() and DeRegDetails.exists(dereg_id):
                    response = DeRegDetails.get_by_id(dereg_id)
                    response = schema.dump(response).data
                else:
                    response = app.json_encoder.encode(DEREG_NOT_FOUND_MSG)

            else:
                response = DeRegDetails.get_all()
                response = schema.dump(response, many=True).data
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
        """POST method handler,
        Create/Submit a new De-Registration details.
        """
        tracking_id = uuid.uuid4()
        try:
            schema = DeRegDetailsSchema()
            args = DeRegDetails.curate_args(request)
            file = request.files.get('file')
            validation_errors = schema.validate(args)
            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            imei_file = Utilities.store_file(file, tracking_id)
            if imei_file:
                return Response(json.dumps(imei_file), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            imei_file = Utilities.process_de_reg_file(file.filename.split("/")[-1], tracking_id, args)
            errored = 'device_count' in imei_file or 'invalid_imeis' in imei_file or \
                      'duplicate_imeis' in imei_file or 'invalid_format' in imei_file

            imeis_list = Utilities.extract_imeis(imei_file)

            if not errored:
                gsma_response = Utilities.get_device_details_by_tac(imei_file)
                response = DeRegDetails.create(args, tracking_id)
                db.session.commit()
                response = schema.dump(response, many=False).data
                log = EsLog.new_request_serialize(response, "DeRegistration", imeis=imeis_list, dereg=True, method="Post")
                EsLog.insert_log(log)
                response = {'request': response, 'devices': gsma_response}
                return Response(json.dumps(response), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:
                return Response(app.json_encoder.encode(imei_file), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            db.session.rollback()
            Utilities.remove_directory(tracking_id)
            app.logger.exception(e)

            data = {
                'message': [_('Registration request failed, check upload path or database connection')]
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()

    @staticmethod
    def put():
        """PUT method handler,
        updates existing de registration request.
        """
        dereg_id = request.form.to_dict().get('dereg_id', None)
        try:
            schema = DeRegDetailsUpdateSchema()
            if dereg_id and dereg_id.isdigit() and DeRegDetails.exists(dereg_id):
                dreg_details = DeRegDetails.get_by_id(dereg_id)
            else:
                return Response(app.json_encoder.encode(DEREG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            args = DeRegDetails.curate_args(request)
            file = request.files.get('file')
            tracking_id = dreg_details.tracking_id
            if dreg_details:
                args.update({'status': dreg_details.status, 'processing_status': dreg_details.processing_status,
                             'report_status': dreg_details.report_status})
            validation_errors = schema.validate(args)
            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            if args.get('close_request', None) == 'True':
                response = DeRegDetails.close(dreg_details)
                if isinstance(response, dict):
                    return Response(app.json_encoder.encode(response), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                else:
                    log = EsLog.new_request_serialize(response, "Close De-Registration", method="Put")
                    EsLog.insert_log(log)
                    response = schema.dump(response, many=False).data
                    return Response(json.dumps(response), status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            if file:
                response = Utilities.store_file(file, tracking_id)
                imeis_list = Utilities.extract_imeis(response)
                if response:
                    return Response(json.dumps(response), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                filename = file.filename
            elif dreg_details.status == Status.get_status_id('New Request'):
                filename = dreg_details.file
                args.update({'device_count': dreg_details.device_count})
            else:
                filename = None

            if filename:
                response = Utilities.process_de_reg_file(filename, tracking_id, args)
                imeis_list = Utilities.extract_imeis(response)
                errored = 'device_count' in response or 'invalid_imeis' in response or \
                          'duplicate_imeis' in response or 'invalid_format' in response
                if not errored:
                    gsma_response = Utilities.get_device_details_by_tac(response)
                    response = DeRegDetails.update(args, dreg_details, file=True)
                    response = schema.dump(response, many=False).data
                    log = EsLog.new_request_serialize(response, "DeRegistration", imeis=imeis_list, dereg=True, method="Put")
                    EsLog.insert_log(log)
                    response = {'request': response, 'devices': gsma_response}
                    return Response(json.dumps(response), status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                else:
                    return Response(app.json_encoder.encode(response), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:
                response = DeRegDetails.update(args, dreg_details, file=False)
                response = schema.dump(response, many=False).data
                log = EsLog.new_request_serialize(response, "DeRegistration", dereg=True, method="Put")
                EsLog.insert_log(log)
                return Response(json.dumps(response), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            db.session.rollback()
            app.logger.exception(e)

            data = {
                'message': [_('Registration request failed, check upload path or database connection')]
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()


class DeRegSectionRoutes(Resource):
    """Class for handling De-Registration Section routes."""

    @staticmethod
    def get(dereg_id):
        """GET method handler, to return all section of a request."""
        try:
            if not dereg_id.isdigit() or not DeRegDetails.exists(dereg_id):
                return Response(app.json_encoder.encode(DEREG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            dereg_details = DeRegDetails.get_by_id(dereg_id)
            dereg_schema = DeRegDetailsSchema()
            doc_schema = DeRegDocumentsSchema()
            device_schema = DeRegDeviceSchema()

            dereg_devices = DeRegDevice.get_devices_by_dereg_id(dereg_id)
            dereg_documents = DeRegDocuments.get_by_reg_id(dereg_id)

            deregistration_data = dereg_schema.dump(dereg_details).data
            device_data = device_schema.dump(dereg_devices, many=True).data
            document_data = doc_schema.dump(dereg_documents, many=True).data

            response = {
                'dereg_details': deregistration_data,
                'dereg_device': device_data,
                'dereg_docs': document_data
            }

            return Response(json.dumps(response), status=CODES.get("OK"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            app.logger.exception(e)

            data = {
                'message': [_('De-Registration request failed, check upload path or database connection')]
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()
