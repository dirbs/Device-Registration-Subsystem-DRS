"""
DRS Registration device resource package.
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
import ast
import uuid

from flask import Response, request
from flask_restful import Resource
from flask_babel import lazy_gettext as _

from app import app, db
from app.api.v1.helpers.error_handlers import REG_NOT_FOUND_MSG, ASSEMBLED_REQUEST_NOT_FOUND_MSG, \
    ASSEMBLED_DEVICES_NOT_FOUND_MSG, ASSEMBLED_REQUEST_DIGIT_MSG
from app.api.v1.helpers.response import MIME_TYPES, CODES
from app.api.v1.models.device import Device
from app.api.v1.models.devicetechnology import DeviceTechnology
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.regdevice import RegDevice
from app.api.v1.models.status import Status
from app.api.v1.models.assembled_devices import Assembled_devices
from app.api.v1.schema.devicedetails import DeviceDetailsSchema
from app.api.v1.schema.localassemblydevicesdetails import AssembledDevicesSchema
from app.api.v1.schema.devicedetailsupdate import DeviceDetailsUpdateSchema
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.helpers.multisimcheck import MultiSimCheck
from app.api.v1.resources.reviewer import SubmitReview
from app.api.v1.models.eslog import EsLog


class AssembledDevicesSearchRoutes(Resource):
    """Class for handling Device Details routes."""

    @staticmethod
    def get(child_reg_id=None):
        """GET method handler, returns device details. If id passed, throws that single record, if no id passed, will pass all records."""

        # schema = DeviceDetailsSchema()

        try:
            if child_reg_id == None:
                data_list = []
                reg_child_devices = Assembled_devices.get_all()
                for reg_child_device in reg_child_devices:
                    serialized_data = Assembled_devices.serialize_data(reg_child_device)

                    if serialized_data:
                        data_list.append(serialized_data)
                db.session.close()
                return Response(json.dumps(data_list), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:
                if not child_reg_id.isdigit() or not Assembled_devices.exists(child_reg_id):
                    return Response(app.json_encoder.encode(ASSEMBLED_REQUEST_NOT_FOUND_MSG),
                                status=CODES.get("UNPROCESSABLE_ENTITY"),mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                reg_child_device = Assembled_devices.get_child_record_with_id(child_reg_id)
                response = reg_child_device if reg_child_device else {}
                db.session.close()
                return Response(json.dumps(response), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            app.logger.exception(e)
            error = {
                'message': [_('Failed to retrieve response, please try later')]
            }
            return Response(app.json_encoder.encode(error), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))

class LocalAssemblyParentSearchRoutes(Resource):
    """Class for handling Device Details routes."""
    @staticmethod
    def get(parent_reg_id):
        """GET method handler, returns child records with parent ID"""

        try:
            if not parent_reg_id.isdigit():
                return Response(app.json_encoder.encode(ASSEMBLED_REQUEST_DIGIT_MSG),
                            status=CODES.get("UNPROCESSABLE_ENTITY"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            if not Assembled_devices.parent_exists(parent_reg_id):
                return Response(app.json_encoder.encode(ASSEMBLED_DEVICES_NOT_FOUND_MSG),
                            status=CODES.get("OK"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            reg_child_devices_with_parent_id = Assembled_devices.get_child_records_with_parent_id(parent_reg_id)
            response = reg_child_devices_with_parent_id if reg_child_devices_with_parent_id else {}
            db.session.close()
            return Response(json.dumps(response), status=CODES.get("OK"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            app.logger.exception(e)
            error = {
                'message': [_('Failed to retrieve response, please try later')]
            }
            return Response(app.json_encoder.encode(error), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))


class AssembledDevicesRoutes(Resource):
    """Class for handling Device Details routes."""

    @staticmethod
    def post():
        """POST method handler, creates a new device."""
        parent_id = request.form.to_dict().get('parent_id', None)

        if not parent_id or not parent_id.isdigit() or not RegDetails.exists(parent_id):
            return Response(app.json_encoder.encode(REG_NOT_FOUND_MSG), status=CODES.get("UNPROCESSABLE_ENTITY"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        try:
            # validate the input field data
            args = request.form.to_dict()
            schema = AssembledDevicesSchema()
            validation_errors = schema.validate(args)
            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            file = request.files.get('file')
            if file == None:
                return Response(json.dumps({"File error": "Please attach a valid TSV file"}),
                                status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            tracking_id = uuid.uuid4()
            file_name = file.filename.split("/")[-1]
            imei_file = Utilities.store_file(file, tracking_id)

            if imei_file:
                return Response(json.dumps(imei_file), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            # get the parent details for cross verification
            parent_reg_details = RegDetails.get_by_id(parent_id)

            imei_file_resp = Utilities.process_assembled_reg_file(file_name, tracking_id, args, parent_reg_details)

            errored = 'imei_per_device' in imei_file_resp or 'device_count' in imei_file_resp or \
                      'invalid_imeis' in imei_file_resp or 'duplicate_imeis' in imei_file_resp or \
                      'missing_imeis' in imei_file_resp or 'limit' in imei_file_resp or \
                      'invalid_format' in imei_file_resp or 'parent_child_imeis_mismatch' in imei_file_resp \
                      or 'parent_child_id_mismatch' in imei_file_resp or 'parent_approved' in imei_file_resp
            if errored:
                return Response(app.json_encoder.encode(imei_file_resp),
                                status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))


            # if file validates and returns IMEIs normalized list
            child_file_normalized_imeis = Utilities.bulk_normalize(imei_file_resp)

            # join list normalized imeis and make a list and check in DB with status other than pending
            whitelisted_imies_list = Utilities.check_bulk_imeis_status(child_file_normalized_imeis, "whitelist")
            if whitelisted_imies_list:
                already_whitelisted = {"already whitelisted" : whitelisted_imies_list}
                return Response(json.dumps(already_whitelisted), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            # Serialize data for data insertion
            assembled_devices_args = Utilities.serialize_data_for_child(args, file)

            # create child record
            reg_child_device = Assembled_devices.create(assembled_devices_args, tracking_id)

            # bulk Update approved IMEIs
            request_id = args.get('parent_id')
            response_approved_imeis = Assembled_devices.bulk_update_approved_imeis(imeis=child_file_normalized_imeis, request_id=request_id, status="whitelist")

            if response_approved_imeis:

                # reg_device = RegDevice.create(args)
                response = schema.dump(reg_child_device, many=False).data

                response["user_id"] = args.get('user_id')
                response['reg_details_id'] = reg_child_device.id
                response['status'] = "whitelisted"
                device_status = 'Whitelisted'
                message = 'Your request for assembled devices with id {id} has been whitelisted'.format(id=reg_child_device.id)

                sr = SubmitReview()
                sr._SubmitReview__generate_notification(user_id=args.get('user_id'), request_id=reg_child_device.id,
                                                        request_type='assembled registration', request_status=10,
                                                        message=message)

                db.session.commit()

                log = EsLog.new_child_device_serialize(response, request_type="Device Child Registration", regdetails=reg_child_device,
                                                 reg_status=device_status, method='Post')
                EsLog.insert_log(log)

                return Response(json.dumps(response), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            else:
                return Response(json.dumps("Record update failure"), status=CODES.get("UNPROCESSABLE_ENTITY"),
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

            if app.config['USE_GSMA_DEVICE_INFO']:
                if reg_details.file:
                    filename = reg_details.file
                    tracking_id = reg_details.tracking_id
                    arguments = {'imei_per_device': reg_details.imei_per_device,
                                 'device_count': reg_details.device_count}
                    m_location = reg_details.m_location
                    get_gsma_info = Utilities.process_reg_file(filename, tracking_id, arguments)
                else:
                    get_gsma_info = ast.literal_eval(reg_details.imeis)
                    m_location = reg_details.m_location

                device = DeviceDetailsRoutes.put_gsma_device_info(get_gsma_info)

                if device:
                    args.update({'brand': device['brand']})
                    args.update({'operating_system': device['operating_system']})
                    args.update({'model_name': device['marketing_name']})
                    args.update({'model_num': device['model_name']})

            if reg_details:
                args.update({'reg_details_id': reg_details.id})
            else:
                args.update({'reg_details_id': ''})

            validation_errors = schema.validate(args)

            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            if reg_details.file:
                filename = reg_details.file
                arg = {'imei_per_device': reg_details.imei_per_device, 'device_count': reg_details.device_count}
                response = Utilities.process_reg_file(filename, reg_details.tracking_id, arg)
            else:
                response = ast.literal_eval(reg_details.imeis)

            message = DeviceDetailsRoutes.multi_sim_validate(response)

            if message is True:
                pass
            elif message is False:
                data = {'message': "Something went wrong while checking multi sim check please try again later!"}
                return Response(app.json_encoder.encode(data), status=CODES.get('UNPROCESSABLE_ENTITY'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            else:
                data = {'message': message}
                return Response(app.json_encoder.encode(data), status=CODES.get('UNPROCESSABLE_ENTITY'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))

            reg_device = RegDevice.create(args)
            reg_device.technologies = DeviceTechnology.create(reg_device.id, args.get('technologies'))
            response = schema.dump(reg_device, many=False).data
            response["user_id"] = args.get('user_id')
            response['reg_details_id'] = reg_details.id

            if m_location == 'local':
                device_status = 'Approved'
            else:
                device_status = 'Pending Review' if app.config['AUTOMATE_IMEI_CHECK'] else 'Awaiting Documents'

            reg_details.update_status(device_status)
            db.session.commit()

            log = EsLog.new_device_serialize(response, request_type="Device Registration", regdetails=reg_details,
                                             reg_status=device_status, method='Post')
            EsLog.insert_log(log)

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
    def multi_sim_validate(response):
        try:
            imeis = []
            for device_imeis in response:
                # Fixed: Converting string to list in ast raise error of leading zero in python3.8
                quotes_removal = [i for i in device_imeis]
                str_repr = str(quotes_removal).strip("[]")
                str_repr = str_repr.replace("'", "")
                str_repr = "['" + str_repr + "']"
                imeis.append(ast.literal_eval(str_repr.replace(' ', '')))

            # multi_sim_result = MultiSimCheck.validate_imeis_capacity(app.config['CORE_BASE_URL'],
            #                                                          app.config['API_VERSION'],
            #                                                          imeis)

            multi_sim_result = MultiSimCheck.validate_imeis_capacity(app.config['CORE_BASE_URL'],
                                                                     app.config['API_VERSION'],
                                                                     imeis)

            if multi_sim_result[0] == 'False':
                message = {}
                i = 0
                for msg in multi_sim_result:
                    if msg == 'False':
                        continue
                    message[i] = msg
                    i += 1
                return message
            elif multi_sim_result[0] is True:
                return True
        except Exception as e:
            app.logger.exception(e)
            return False

    @staticmethod
    def put_gsma_device_info(get_gsma_info):
        device = {}
        for tac in get_gsma_info:
            get_gsma_info = tac[0][:8]
            break

        device_info = Utilities.get_gsma_device(get_gsma_info)

        if device_info['results'][0]['gsma'] and device_info['results'][0]['gsma'] is not None:
            device_info = device_info['results'][0]['gsma']
            device["brand"] = device_info['brand_name']
            device["operating_system"] = device_info['operating_system']
            device["model_name"] = device_info['model_name']
            device["marketing_name"] = device_info['marketing_name']
            return device
        else:
            return False

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

            if app.config['USE_GSMA_DEVICE_INFO']:
                if reg_details.file:
                    filename = reg_details.file
                    tracking_id = reg_details.tracking_id
                    arguments = {'imei_per_device': reg_details.imei_per_device,
                                 'device_count': reg_details.device_count}
                    get_gsma_info = Utilities.process_reg_file(filename, tracking_id, arguments)
                else:
                    get_gsma_info = ast.literal_eval(reg_details.imeis)

                device = DeviceDetailsRoutes.put_gsma_device_info(get_gsma_info)

                if device:
                    args.update({'brand': device['brand']})
                    args.update({'operating_system': device['operating_system']})
                    args.update({'model_name': device['marketing_name']})
                    args.update({'model_num': device['model_name']})

            if reg_details:
                args.update({'reg_details_id': reg_details.id, 'status': reg_details.status})
            else:
                args.update({'reg_details_id': ''})
            validation_errors = schema.validate(args)
            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            if reg_details.file:
                filename = reg_details.file
                args = {'imei_per_device': reg_details.imei_per_device, 'device_count': reg_details.device_count}
                response = Utilities.process_reg_file(filename, reg_details.tracking_id, args)
            else:
                response = ast.literal_eval(reg_details.imeis)

            message = DeviceDetailsRoutes.multi_sim_validate(response)

            if message is True:
                pass
            elif message is False:
                data = {'message': "Something went wrong while checking multi sim check please try again later!"}
                return Response(app.json_encoder.encode(data), status=CODES.get('UNPROCESSABLE_ENTITY'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            else:
                data = {'message': message}
                return Response(app.json_encoder.encode(data), status=CODES.get('UNPROCESSABLE_ENTITY'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))

            processing_failed = reg_details.processing_status in [Status.get_status_id('Failed'),
                                                                  Status.get_status_id('New Request'),
                                                                  Status.get_status_id('Pending Review')]
            report_failed = reg_details.report_status == Status.get_status_id('Failed')
            processing_required = processing_failed or report_failed

            response = schema.dump(reg_device, many=False).data
            response['id'] = reg_device.id
            device_status = 'Pending Review' if app.config['AUTOMATE_IMEI_CHECK'] else 'Awaiting Documents'

            log = EsLog.new_device_serialize(response, request_type="Update Device Registration", regdetails=reg_details,
                                             reg_status=device_status, method='Put')
            EsLog.insert_log(log)

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
