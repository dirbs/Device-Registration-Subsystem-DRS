"""
DRS healthcheck resource module.
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
import ast
import requests
import time


from flask import Response, request
from flask_apispec import MethodResource
from flask_babel import lazy_gettext as _

from app.api.v1.models.deregdetails import DeRegDetails
from app import app, db, GLOBAL_CONF
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.schema.ussd import RegistrationDetailsSchema, UssdTrackingSchema, UssdDeleteSchema, UssdCountSchema
from app.api.v1.resources.regdevicedetails import DeviceDetailsRoutes
from app.api.v1.models.ussd import UssdModel

from app.api.v1.models.device import Device

from app.api.v1.helpers.response import MIME_TYPES, CODES
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.helpers.ussd_helper import Ussd_helper

from app.metadata import version, db_schema_version
from app.api.v1.schema.version import VersionSchema

from app.api.v1.helpers.key_cloak import Key_cloak
from app.api.v1.helpers.sms import Jasmin

from app.api.v1.models.regdevice import RegDevice
from app.api.v1.models.devicetechnology import DeviceTechnology
from app.api.v1.models.devicequota import DeviceQuota as DeviceQuotaModel

from app.api.v1.models.eslog import EsLog
from app.api.v1.schema.regdetails import RegistrationDetailsSchema as rdSchema
from app.api.v1.schema.devicedetails import DeviceDetailsSchema


class Register_ussd(MethodResource):
    """Class for handling version api resources."""

    messages_list = []

    def get(self):
        """GET method handler."""
        return Response(json.dumps(
            VersionSchema().dump(dict(
                version=version,
                db_schema_version=db_schema_version
            )).data))

    def post(self):
        """POST method handler, creates registration requests."""
        tracking_id = uuid.uuid4()
        try:
            # get the posted data

            args = RegDetails.curate_args(request)

            # create Marshmallow object
            schema = RegistrationDetailsSchema()

            # validate CNIC number
            if not args['cnic'] or not args['cnic'].isdigit():
                messages = {
                    'from': 'DRS-USSD',
                    'to': args['msisdn'],
                    'content': "CNIC number is mandatory and must be digits only."
                }
                self.messages_list.append(messages.copy())

                print("Printing the jasmin message")
                print(messages)

                jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                app.logger.info("Jasmin API response: " + str(jasmin_send_response.status_code))

                return Response(app.json_encoder.encode({"message": "CNIC number is mandatory and must be digits only."}), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

            # Multi SIM Validation
            response = ast.literal_eval(args['imeis'])

            message = DeviceDetailsRoutes.multi_sim_validate(response)
            if message is True:
                pass
            elif message is False:
                messages = {
                    'from': 'DRS-USSD',
                    'to': args['msisdn'],
                    'content': "Something went wrong, please try again later"
                }
                self.messages_list.append(messages.copy())

                print("Printing the jasmin message")
                print(self.messages_list)

                jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                app.logger.info("Jasmin API response: " + str(jasmin_send_response.status_code))

                data = {'message': "Something went wrong while checking multi sim check please try again later!"}
                return Response(app.json_encoder.encode(data), status=CODES.get('UNPROCESSABLE_ENTITY'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            else:
                # create messages for user if any
                changed_msgs = []
                for key1, val1 in message.items():
                    for key2, val2 in val1.items():
                        val2 = Ussd_helper.check_forbidden_string(val2)
                        changed_dict = {key2:val2}
                        changed_msgs.append(changed_dict)
                        messages = {
                            'from': 'DRS-USSD',
                            'to': args['msisdn'],
                            'content': val2
                        }
                        self.messages_list.append(messages.copy())
                # message = changed_msgs

                print("Printing the jasmin message")
                print(self.messages_list)

                jasmin_send_response = Jasmin.send_batch(self.messages_list, network = args['network'])
                app.logger.info("Jasmin API response: " + str(jasmin_send_response.status_code))

                data = {'message': changed_msgs}
                return Response(app.json_encoder.encode(data), status=CODES.get('UNPROCESSABLE_ENTITY'),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))

            # validate posted data
            validation_errors = schema.validate(args)

            if validation_errors:
                for key, value in validation_errors.items():

                    str_val = ''
                    if key == "imeis":
                        if isinstance(value[0], dict):
                            for k_i, v_i in value[0].items():
                                str_val = str_val + str(v_i[0] + ' ' + args['imeis'][0][k_i])+". "
                        else:
                            print(validation_errors)
                            str_val = str_val + str(value[0])
                    else:
                        if key == "msisdn":
                            if isinstance(value, list):
                                str_val = str_val + str(value[0])

                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': key +':' + str(value[0]) if not dict else str(str_val)
                    }
                    self.messages_list.append(messages.copy())

                print("Printing the jasmin messages")
                print(self.messages_list)

                jasmin_send_response = Jasmin.send_batch(self.messages_list, network = args['network'])
                app.logger.info("Jasmin API response: " + str(jasmin_send_response.status_code))
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:

                # call KeyCloak for admin Token
                admin_token_data = Key_cloak.get_admin_token()

                # call KeyCloak with token for
                user_data = Key_cloak.check_user_get_data(args, admin_token_data)

                # if user is created, a password is set for it
                arguments = Ussd_helper.set_args_dict_for_regdetails(args, user_data)

                reg_response = RegDetails.create(arguments, tracking_id)

                db.session.commit()

                # get GSMA information and make device call. we get the device id
                if reg_response.id:
                    schema2 = rdSchema()
                    response = schema2.dump(reg_response, many=False).data

                    # Todo: add logging here or below after condition check
                    log = EsLog.new_request_serialize(response, 'USSD Registration', method='Post',
                                                imeis=arguments['imeis'])
                    EsLog.insert_log(log)

                    # get the tac from an imei in the dict and search for GSMA record
                    tac = arguments['imeis'][0][0][0:8]
                    gsma_url = str(app.config['CORE_BASE_URL']+app.config['API_VERSION'])+str('/tac/'+tac)

                    # get GSMA record against each TAC and match them with IMEIs count given in list
                    gsma_response = requests.get(gsma_url).json()

                    if gsma_response["gsma"] is None:
                        # GSMA record not found for the said TAC
                        messages = {
                            'from': 'DRS-USSD',
                            'to': args['msisdn'],
                            'content': "No record found for TAC:" + str(tac)
                        }
                        self.messages_list.append(messages.copy())

                        print("Printing the jasmin messages")
                        print(self.messages_list)

                        jasmin_send_response = Jasmin.send_batch(self.messages_list, network = args['network'])
                        app.logger.info("Jasmin API response: " + str(jasmin_send_response.status_code))

                        data = {'message': messages['content']}

                        return Response(app.json_encoder.encode(data), status=CODES.get('UNPROCESSABLE_ENTITY'),
                                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))

                    else:

                        # set device data args
                        device_arguments = Ussd_helper.set_args_dict_for_devicedetails(reg_response, arguments, gsma_response)

                        reg_details = RegDetails.get_by_id(reg_response.id)

                        if reg_details:
                            device_arguments.update({'reg_details_id': reg_details.id})
                        else:
                            device_arguments.update({'reg_details_id': ''})

                        device_arguments.update({'device_type': 'Smartphone'})

                        reg_device = RegDevice.create(device_arguments)

                        reg_device.technologies = DeviceTechnology.create(
                            reg_device.id, device_arguments.get('technologies'), True)

                        device_status = 'Pending Review'

                        reg_details.update_status(device_status)

                        DeviceQuotaModel.get_or_create(reg_response.user_id, 'ussd')

                        Utilities.create_directory(tracking_id)

                        db.session.commit()

                        device_schema = DeviceDetailsSchema()
                        device_serialize_data = device_schema.dump(reg_device, many=False).data
                        log = EsLog.new_device_serialize(device_serialize_data, request_type="USSD Device Registration",
                                                         regdetails=reg_details,
                                                         reg_status=device_status, method='Post')
                        EsLog.insert_log(log)

                        Device.create(reg_details, reg_device.id, ussd=True)

                        # delay the process 5 seconds to complete the process
                        time.sleep(5)

                        # get the device details
                        reg_details = RegDetails.get_by_id(reg_response.id)

                        status_msg = Ussd_helper.set_message_for_user_info(reg_details.status)

                        # if reg_details.status == 6:
                        status_msg = status_msg + " Your device tracking id is: " + str(reg_details.id)

                        # send user a details about device
                        messages = {
                            'from': 'DRS-USSD',
                            'to': args['msisdn'],
                            'content': status_msg
                        }
                        self.messages_list.append(messages.copy())

                        # send username and password to the new user
                        if 'password' in user_data:
                            messages = {
                                'from': 'DRS-USSD',
                                'to': args['msisdn'],
                                'content': "New user credentials are, username: " + arguments[
                                    'username'] + " and password: " +
                                           arguments['password']
                            }
                            self.messages_list.append(messages.copy())

                        jasmin_send_response = Jasmin.send_batch(self.messages_list, network = args['network'])
                        app.logger.info("Jasmin API response: " + str(jasmin_send_response.status_code))
                        app.logger.info("Printing the message array in CLI mode.")
                        app.logger.info(self.messages_list)
                        response = {
                            'message': 'Device registration has been processed successfully.'
                        }

                        if status_msg:
                            response['status_response'] = status_msg
                        return Response(json.dumps(response), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get("APPLICATION_JSON"))

                else:
                    # error in regdetails
                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': "Registration request failed, check upload path or database connection"
                    }
                    self.messages_list.append(messages.copy())

                    jasmin_send_response = Jasmin.send_batch(self.messages_list, network = args['network'])
                    app.logger.info("Jasmin API response: " + str(jasmin_send_response.status_code))

                    # response = schema.dump(response, many=False).data
                    data = {'message': [_('Device undergone the process. Please hold your breath.')]}
                    return Response(app.json_encoder.encode(data), status=CODES.get('UNPROCESSABLE_ENTITY'),
                                    mimetype=MIME_TYPES.get('APPLICATION_JSON'))
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


# Track down the records for a user
class Track_record_ussd(MethodResource):
    """Class for handling USSD based tracking."""

    messages_list = []

    def get(self):
        """GET method handler."""
        return Response(json.dumps(
            VersionSchema().dump(dict(
                version=version,
                db_schema_version=db_schema_version
            )).data))

    def post(self):
        """POST method handler, track USSD based Registered devices."""
        try:

            # get the posted data
            args = RegDetails.curate_args(request)

            # create Marshmallow object
            schema = UssdTrackingSchema()

            # validate posted data
            validation_errors = schema.validate(args)

            if validation_errors:

                for key, value in validation_errors.items():
                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': key + ':' + value[0]
                    }
                    self.messages_list.append(messages.copy())

                jasmin_send_response = Jasmin.send_batch(self.messages_list, network = args['network'])
                print("Jasmin API response: " + str(jasmin_send_response.status_code))
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:

                # check device record
                dev_result = UssdModel.exists(args['device_id'])

                if dev_result == True:
                    # if record matches with the passed MSISDN
                    device_info = UssdModel.get_by_id(args['device_id'])

                    if device_info.msisdn != args['msisdn']:
                        messages = {
                            'from': 'DRS-USSD',
                            'to': args['msisdn'],
                            'content': "Your MSISDN does not match with the record."
                        }
                        self.messages_list.append(messages.copy())

                        jasmin_send_response = Jasmin.send_batch(self.messages_list, network = args['network'])
                        print("Jasmin API response: " + str(jasmin_send_response.status_code))

                        data = {'message': [_("Your MSISDN does not match with the record.")]}
                        return Response(app.json_encoder.encode(data),
                                        status=CODES.get("RECORD_MISMATCH"),
                                        mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                    else:
                        msg_string = Ussd_helper.set_record_info(device_info, True)
                        print(msg_string)

                        messages = {
                            'from': 'DRS-USSD',
                            'to': args['msisdn'],
                            'content': str(msg_string)
                        }
                        self.messages_list.append(messages.copy())

                    jasmin_send_response = Jasmin.send_batch(self.messages_list, network = args['network'])
                    print("printing the jasmin send response code in track")
                    print(jasmin_send_response.status_code)
                    print("Jasmin API response: " + str(jasmin_send_response.status_code))

                    data = {'message': [_(msg_string)]}
                    return Response(app.json_encoder.encode(data),
                                    status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))

                else:
                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': 'No record found with that Device ID'
                    }
                    self.messages_list.append(messages.copy())

                    jasmin_send_response = Jasmin.send_batch(self.messages_list, network = args['network'])
                    print("Jasmin API response: " + str(jasmin_send_response.status_code))

                    data = {'message': [_('No record found with that ID')]}
                    return Response(app.json_encoder.encode(data),
                                    status=CODES.get("RECORD_NOT_FOUND"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        except Exception as e:  # pragma: no cover
            db.session.rollback()
            app.logger.exception(e)
            data = {
                'message': [_('Something went wrong. Please try again later.')]
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()


# Delete a record
class Delete_record_ussd(MethodResource):
    """Class for handling USSD based Deletion"""

    messages_list = []

    def get(self):
        """GET method handler."""
        return Response(json.dumps(
            VersionSchema().dump(dict(
                version=version,
                db_schema_version=db_schema_version
            )).data))

    # @staticmethod
    def put(self):
        """PUT method handler, updates existing registration request. """
        try:

            # get the posted data
            args = RegDetails.curate_args(request)

            # create Marshmallow object
            schema = UssdDeleteSchema()

            # validate posted data
            validation_errors = schema.validate(args)

            if validation_errors:

                for key, value in validation_errors.items():
                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': key + ':' + value[0]
                    }
                    self.messages_list.append(messages.copy())

                jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                print("Jasmin API response: " + str(jasmin_send_response.status_code))
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:

                dereg_id = args['device_id']

                if dereg_id and dereg_id.isdigit() and RegDetails.exists(dereg_id):

                    # if record matches with the passed MSISDN
                    device_info = UssdModel.get_by_id(dereg_id)

                    if device_info.msisdn != args['msisdn']:
                        messages = {
                            'from': 'DRS-USSD',
                            'to': args['msisdn'],
                            'content': "Your MSISDN does not match with the record."
                        }
                        self.messages_list.append(messages.copy())

                        jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                        print("Jasmin API response: " + str(jasmin_send_response.status_code))

                        data = {'message': [_("Your MSISDN does not match with the record.")]}
                        return Response(app.json_encoder.encode(data),
                                        status=CODES.get("RECORD_MISMATCH"),
                                        mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                    else:
                        dreg_details = RegDetails.get_by_id(dereg_id)
                else:

                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': 'Delete Request not found.'
                    }
                    self.messages_list.append(messages.copy())

                    jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                    print("Printing the jasmin send response")
                    print(jasmin_send_response)

                    if jasmin_send_response:
                        print("Jasmin API response: " + str(jasmin_send_response.status_code))
                    else:
                        print("Jasmin API response: " + str(jasmin_send_response))
                    return Response(app.json_encoder.encode({'message': [_('Delete Request not found.')]}),
                                    status=CODES.get("UNPROCESSABLE_ENTITY"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                if dreg_details:
                    normalized_imeis = Ussd_helper.get_normalized_imeis(dreg_details.imeis)
                    Utilities.de_register_imeis(normalized_imeis)
                    args.update({'status': dreg_details.status, 'processing_status': dreg_details.processing_status,
                                 'report_status': dreg_details.report_status})
                validation_errors = schema.validate(args)
                if validation_errors:
                    for key, value in validation_errors.items():
                        messages = {
                            'from': 'DRS-USSD',
                            'to': args['msisdn'],
                            'content': key + ':' + value[0]
                        }
                        self.messages_list.append(messages.copy())

                    jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                    print("Jasmin API response: " + str(jasmin_send_response.status_code))
                    return Response(app.json_encoder.encode(validation_errors),
                                    status=CODES.get("UNPROCESSABLE_ENTITY"),
                                    mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                if args.get('close_request', None) == 'True':

                    response = DeRegDetails.close(dreg_details)

                    if isinstance(response, dict):

                        # let the user know about the deregistration
                        messages = {
                            'from': 'DRS-USSD',
                            'to': args['msisdn'],
                            'content': str(response['message'])
                        }

                        self.messages_list.append(messages.copy())

                        jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])

                        print("Jasmin API response: " + str(jasmin_send_response.status_code))
                        print(str(response['message']))

                        return Response(app.json_encoder.encode(response), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                        mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                    else:
                        log = EsLog.new_request_serialize(dreg_details, 'USSD De-Registration', method='Put')
                        EsLog.insert_log(log)

                        response = schema.dump(response, many=False).data
                        # let the user know about the deregistration
                        messages = {
                            'from': 'DRS-USSD',
                            'to': args['msisdn'],
                            'content': str("Device with ID: " + str(dereg_id) + " has been DeRegistered")
                        }

                        self.messages_list.append(messages.copy())

                        jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                        print("Jasmin API response: " + str(jasmin_send_response.status_code))
                        response['response'] = messages['content']

                        return Response(json.dumps(response), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get("APPLICATION_JSON"))

                response = DeRegDetails.update(args, dreg_details, file=False)

                response = schema.dump(response, many=False).data

                # let the user know about the deregistration
                messages = {
                    'from': 'DRS-USSD',
                    'to': args['msisdn'],
                    'content': str(response['message'])
                }

                jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                self.messages_list.append(messages.copy())

                print("Jasmin API response: " + str(jasmin_send_response.status_code))
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

# count records
class Ussd_records_count(MethodResource):
    """Class for handling USSD based Registration Count"""

    messages_list = []

    def get(self):
        """GET method handler."""
        return Response(json.dumps(
            VersionSchema().dump(dict(
                version=version,
                db_schema_version=db_schema_version
            )).data))

    def post(self):
        """POST method handler, Get all user's registered devices and statuses"""
        try:

            # get the posted data
            args = RegDetails.curate_args(request)

            # create Marshmallow object
            schema = UssdCountSchema()

            # validate posted data
            validation_errors = schema.validate(args)

            if validation_errors:

                for key, value in validation_errors.items():
                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': key + ':' + value[0]
                    }
                    self.messages_list.append(messages.copy())

                jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                print("Jasmin API response: " + str(jasmin_send_response.status_code))
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:
                total_count = RegDetails.get_count(msisdn=args['msisdn'])

                if total_count['count_with_msisdn'] > 0:
                    msisdn_all_counts = RegDetails.get_all_counts(msisdn=args['msisdn'])
                    msisdn_all_counts.update({"count_with_msisdn": total_count['count_with_msisdn']})

                    message = Ussd_helper.set_count_message(msisdn_all_counts)

                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': str(message)
                    }
                    self.messages_list.append(messages.copy())

                    jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                    print("Jasmin API response: " + str(jasmin_send_response.status_code))
                    data = {'message': [_(str(message))]}
                else:

                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': "No records found with that number."
                    }
                    self.messages_list.append(messages.copy())

                    jasmin_send_response = Jasmin.send_batch(self.messages_list, network=args['network'])
                    print("Jasmin API response: " + str(jasmin_send_response.status_code))
                    data = {'message': [_("No records found with that number.")]}

                return Response(app.json_encoder.encode(data),
                                status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        except Exception as e:
            db.session.rollback()
            app.logger.exception(e)

            data = {
                'message': [_('Registration request failed, check upload path or database connection')]
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()

