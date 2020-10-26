"""
DRS search resource package.
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
from app import app
import json
from flask import request, Response
from flask_babel import lazy_gettext as _
from flask_restful import Resource
from app.api.v1.helpers.search_registration import SearchRegistraion
from app.api.v1.helpers.search_deregistration import SearchDeregistration
from app.api.v1.helpers.response import MIME_TYPES, CODES


class Search(Resource):
    """Class for handling Search routes."""

    @staticmethod
    def post():
        """POST method handler."""
        args = request.get_json()
        data = {
            "start": args.get('start', 1),
            "previous": "",
            "next": "",
            "requests": [],
            "count": 0,
            "limit": args.get('limit', 2),
            "message": ""
        }

        if args.get("search_specs") is not None:
            request_data = args.get("search_specs")
            if 'group' not in request_data or 'request_type' \
                    not in request_data \
                    or 'user_id' not in request_data:
                data['message'] = 'Search Specs attributes missing!'
                response = Response(json.dumps(data), status=CODES.get("NOT_FOUND"),
                                    mimetype=MIME_TYPES.get('APPLICATION_JSON'))

                return response

        try:
            if request_data['group'] == 'importer':

                if request_data['request_type'] == 1:
                    return SearchRegistraion.get_result(request, request_data['group'])
                else:
                    data['message']="Request type not found!"
                    response = Response(json.dumps(data), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))

                    return response

            elif request_data['group'] == 'exporter':
                if request_data['request_type'] == 2:
                    return SearchDeregistration.get_result(request,request_data['group'])
                else:
                    data['message'] = "Request type not found!"
                    response = Response(json.dumps(data), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                    return response

            elif request_data['group'] == 'individual':
                if request_data['request_type'] == 1:
                    return SearchRegistraion.get_result(request, request_data['group'])
                else:
                    data['message'] = "Request type not found!"
                    response = Response(json.dumps(data), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                    return response

            elif request_data['group'] == 'reviewer':
                if request_data['request_type'] == 1:
                    return SearchRegistraion.get_result(request, request_data['group'])
                elif request_data['request_type'] == 2:
                    return SearchDeregistration.get_result(request, request_data['group'])
                else:
                    data['message'] = "Request type not found!"
                    response = Response(json.dumps(data), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                    return response
            else:
                data['message'].append("No Data Found")
                response = Response(json.dumps(data), status=CODES.get("OK"),
                                    mimetype=MIME_TYPES.get('APPLICATION_JSON'))

                return response

        except Exception as ex:
            app.logger.exception(ex)
            data['message'] = "No data found"
            response = Response(json.dumps(data), status=CODES.get("NOT_FOUND"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))

            return response
