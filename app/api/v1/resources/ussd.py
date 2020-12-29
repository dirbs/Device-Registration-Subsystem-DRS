"""
DRS healthcheck resource module.
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
import uuid

from pprint import pprint

from flask import Response, request
from flask_apispec import marshal_with, doc, MethodResource
from flask_restful import Resource
from flask_babel import lazy_gettext as _


from app import app, db
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.schema.ussd import RegistrationDetailsSchema

from app.api.v1.helpers.response import MIME_TYPES, CODES
from app.api.v1.helpers.utilities import Utilities

from app.metadata import version, db_schema_version
from app.api.v1.schema.version import VersionSchema

from app.api.v1.helpers.key_cloak import Key_cloak
from app.api.v1.helpers.sms import Jasmin


from app.api.v1.schema.reviewer import ErrorResponse
from marshmallow import Schema, fields, validates, ValidationError, post_dump, validate, pre_dump


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

            # validate posted data
            validation_errors = schema.validate(args)

            if validation_errors:

                for key, value in validation_errors.items():
                    messages = {
                        'from': 'DRS-USSD',
                        'to': args['msisdn'],
                        'content': key +' : ' + value[0]
                    }
                    self.messages_list.append(messages.copy())

                jasmin_send_response = Jasmin.send_batch(self.messages_list)
                print("Jasmin API response: " + str(jasmin_send_response.status_code))
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:

                # call KeyCloak for admin Token
                admin_token_data = Key_cloak.get_admin_token()

                # call KeyCloak with token for
                user_data = Key_cloak.check_user_get_data(args, admin_token_data)

                print('\n' * 5)
                print("printing the user_data")
                pprint(user_data)

                print('\n' * 5)
                print("printing the args data")
                pprint(args)

                # pass
                # get admin token using api call to keycloak and send user CNIC to keycloak to fetch user if any
                # or create a user

                # Utilities.create_directory(tracking_id)
                print("are we here in the registration line? ")
                response = RegDetails.create(args, tracking_id)
                db.session.commit()
                response = schema.dump(response, many=False).data
                return Response(json.dumps(response), status=CODES.get("OK"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))

        except Exception as e:  # pragma: no cover
            db.session.rollback()
            app.logger.exception(e)
            # Utilities.remove_directory(tracking_id)
            app.logger.exception(e)

            data = {
                'message': [_('Registration request failed, check upload path or database connection')]
            }

            return Response(app.json_encoder.encode(data), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()