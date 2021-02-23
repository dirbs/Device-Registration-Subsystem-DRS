"""
DRS Registration resource package.
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

from flask import Response
from flask_apispec import MethodResource, use_kwargs

from app import app, db
from ..models.association import ImeiAssociation
from ..models.approvedimeis import ApprovedImeis
from ..schema.association import AssociateImeisSchema, AssociateDuplicateImeisSchema
from ..helpers.response import CODES, MIME_TYPES


class AssociateImeis(MethodResource):
    """Class for handling Association Requests routes."""

    @use_kwargs(AssociateImeisSchema().fields_dict, locations=['json'])
    def post(self, **kwargs):
        """POST method handler, returns association requests."""
        try:
            schema = AssociateImeisSchema()
            validation_errors = schema.validate(kwargs)
            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:
                associated_devices = len(ImeiAssociation.get_imei_by_uid(kwargs.get('uid'))) if len(ImeiAssociation.get_imei_by_uid(kwargs.get('uid'))) is not None else int(0)
                if associated_devices < app.config.get('ASSOCIATION_LIMIT'):
                    if ApprovedImeis.registered(kwargs.get('imei')):
                        if ImeiAssociation.associated(kwargs.get('imei')):
                            if ImeiAssociation.detect_duplicate(kwargs.get('imei'), kwargs.get('uid')):
                                return Response(json.dumps({"message": "IMEI already associated wih the same uid"}),
                                                status=CODES.get("CONFLICT"), mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                            elif app.config.get('GRACE_PERIOD'):
                                return Response(
                                    json.dumps(
                                        {"message": "IMEI already associated you want to associate duplicate?",
                                         "is_associated": True}),
                                    status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                            else:
                                return Response(json.dumps({"message": "imei already associated"}), status=CODES.get("CONFLICT"),
                                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                        else:
                            ImeiAssociation(imei=kwargs.get('imei'), uid=kwargs.get('uid'), duplicate=False).add()
                            return Response(json.dumps({"message": "IMEI has been associated with the given Uid"}),
                                            status=CODES.get("OK"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                    else:
                        return Response(json.dumps({"message": "IMEI not registered please register first"}),
                                        status=CODES.get("NOT_ACCEPTABLE"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                else:
                    return Response(
                        json.dumps({"message": "Maximum number of devices have already been associated with this UID"}),
                        status=CODES.get("NOT_ACCEPTABLE"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            app.logger.exception(e)
            error = {
                'message': ['Failed to associate IMEI, please try later']
            }
            return Response(app.json_encoder.encode(error), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()

    def get(self, uid):
        """GET method handler, returns list IMEI associated with given UID."""
        try:
            response = ImeiAssociation.get_imei_by_uid(uid)
            associations = [{"imei":row.imei, "uid":row.uid, "start_date":row.start_date.strftime("%Y-%m-%d %H:%M:%S")} for row in response]
            return Response(json.dumps(associations), status=CODES.get("OK"),
                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            app.logger.exception(e)
            error = {
                'message': ['Failed to retrieve associated IMEIs, please try later']
            }
            return Response(app.json_encoder.encode(error), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()


class AssociateDuplicate(MethodResource):
    """Class for handling Duplicate Association Requests routes."""

    @use_kwargs(AssociateDuplicateImeisSchema().fields_dict, locations=['json'])
    def post(self, **kwargs):
        """POST method handler, returns duplicate association requests."""
        try:
            schema = AssociateDuplicateImeisSchema()
            validation_errors = schema.validate(kwargs)
            if validation_errors:
                return Response(app.json_encoder.encode(validation_errors), status=CODES.get("UNPROCESSABLE_ENTITY"),
                                mimetype=MIME_TYPES.get("APPLICATION_JSON"))
            else:
                if kwargs.get('choice'):
                    associated_devices = len(ImeiAssociation.get_imei_by_uid(kwargs.get('uid'))) if len(ImeiAssociation.get_imei_by_uid(kwargs.get('uid'))) is not None else int(0)
                    if associated_devices < app.config.get('ASSOCIATION_LIMIT'):
                        if ApprovedImeis.registered(kwargs.get('imei')):
                            if ImeiAssociation.associated(kwargs.get('imei')):
                                if ImeiAssociation.detect_duplicate(kwargs.get('imei'), kwargs.get('uid')):
                                    return Response(json.dumps({"message": "IMEI already associated wih the same uid"}),
                                                    status=CODES.get("CONFLICT"),
                                                    mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                                elif app.config.get('GRACE_PERIOD'):
                                    ImeiAssociation(imei=kwargs.get('imei'), uid=kwargs.get('uid'), duplicate=True).add()
                                    return Response(json.dumps({"message": "IMEI has been associated as duplicate."}),
                                                    status=CODES.get("OK"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                                else:
                                    return Response(json.dumps({"message": "duplicate IMEI cannot be associated"}),
                                                    status=CODES.get("CONFLICT"),
                                                    mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                            else:
                                return Response(json.dumps({"message": "IMEI not associated hence cannot be associated as duplicate."}),
                                                status=CODES.get("OK"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                        else:
                            return Response(json.dumps({"message": "IMEI not registered please register first"}),
                                            status=CODES.get("NOT_ACCEPTABLE"),
                                            mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                    else:
                        return Response(
                            json.dumps(
                                {"message": "Maximum number of devices have already been associated with this UID"}),
                            status=CODES.get("NOT_ACCEPTABLE"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
                else:
                    return Response(json.dumps({"message": "OK."}),
                                    status=CODES.get("CONFLICT"), mimetype=MIME_TYPES.get("APPLICATION_JSON"))
        except Exception as e:  # pragma: no cover
            app.logger.exception(e)
            error = {
                'message': ['Failed to associate duplicate IMEI, please try later']
            }
            return Response(app.json_encoder.encode(error), status=CODES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('APPLICATION_JSON'))
        finally:
            db.session.close()
