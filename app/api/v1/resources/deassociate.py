"""
DRS Registration resource package.
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
from flask_apispec import MethodResource, use_kwargs

from app import app, db
from ..models.association import ImeiAssociation
from ..schema.association import AssociateImeisSchema
from ..helpers.response import CODES, MIME_TYPES


class DeassociateImeis(MethodResource):
    """Class for handling De-association Requests routes."""

    @use_kwargs(AssociateImeisSchema().fields_dict, locations=['json'])
    def post(self, **kwargs):
        """POST method handler, returns de-association requests."""
        try:
            schema = AssociateImeisSchema()
            validation_errors = schema.validate(kwargs)
            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            elif ImeiAssociation.exists(kwargs.get('imei')):
                pair_exists = ImeiAssociation.deassociate(kwargs.get('imei'), kwargs.get('uid'))
                if pair_exists is 200:
                    return Response(json.dumps({"message": "IMEI "+kwargs.get('imei')+" has been de-associated."}),
                                    status=CODES.get("OK"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                elif pair_exists == 409:
                    return Response(
                        json.dumps({"message": "IMEI " + kwargs.get('imei') + " not associated with given UID."}),
                        status=CODES.get("CONFLICT"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                else:
                    return Response(
                        json.dumps({"message": "IMEI " + kwargs.get('imei') + " has already been de-associated."}),
                        status=CODES.get("NOT_ACCEPTABLE"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:
                return Response(
                    json.dumps({"message":"IMEI "+kwargs.get('imei')+" does not exist hence cannot be de-associated."}),
                    status=CODES.get("OK"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            app.logger.exception(e)
            error = {
                'message': ['Failed to de-associate IMEI, please try later']
            }
            return Response(app.json_encoder.encode(error), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()
