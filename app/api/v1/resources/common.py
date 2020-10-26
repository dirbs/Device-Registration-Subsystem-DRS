"""
DRS common resource package.
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
import os
import json
from urllib.parse import unquote

from flask import send_file, Response
from flask_apispec import marshal_with, doc, MethodResource, use_kwargs
from flask_restful import Resource
from flask_babel import lazy_gettext as _

from app import app
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.models.devicetype import DeviceType
from app.api.v1.models.documents import Documents
from app.api.v1.models.status import Status
from app.api.v1.models.technologies import Technologies
from app.api.v1.schema.common import FileArgs, ServerConfigs as ServerConfigSchema
from app.api.v1.schema.reviewer import ErrorResponse


class BaseRoutes(Resource):
    """Sample files format for registration and
    de-registration"""

    @staticmethod
    def get(request_type):
        """GET method handler for sample files route."""
        if request_type == 'registration':
            file_path = Utilities.reg_sample_file
        else:
            file_path = Utilities.dereg_sample_file
        return send_file(file_path)


class Files(MethodResource):
    """Class for handling files routes."""

    @doc(description='To download files using valid paths', tags=['Files'])
    @marshal_with(None, code=200, description='On success (file downloading)')
    @marshal_with(ErrorResponse, code=400, description='On Error (Invalid path, bad request)')
    @marshal_with(ErrorResponse, code=422, description='On Error (Missing/Invalid arguments)')
    @marshal_with(ErrorResponse, code=500, description='On Error (Internal server error)')
    @use_kwargs(FileArgs().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """GET method handler for downloading files with paths."""
        path = unquote(kwargs.get('path'))

        if path is None or not path:
            err = {'error': [_('path cannot be empty')]}
            return Response(app.json_encoder.encode(ErrorResponse().dump(err).data),
                            status=422, mimetype='application/json')
        if os.path.isfile(path):
            try:
                return send_file(path, as_attachment=True)
            except Exception as e:
                app.logger.exception(e)
                res = {'error': [_('Unable to process the request')]}
                return Response(app.json_encoder.encode(ErrorResponse().dump(res).data),
                                status=500, mimetype='application/json')
        else:
            res = {'error': [_('file not found or bad file path')]}
            return Response(app.json_encoder.encode(ErrorResponse().dump(res).data),
                            status=400, mimetype='application/json')


class ServerConfigs(MethodResource):
    """Class for handling server configuration routes."""

    @doc(description='To return different configuration parameters from server', tags=['Configurations'])
    @marshal_with(ServerConfigSchema, code=200, description='On success (Successful response)')
    def get(self):
        """GET method handler for server-configs."""
        technologies = Technologies.get_technologies()
        device_types = DeviceType.get_device_types()
        status_types = Status.get_status_types()

        system_configs = {
            'label': 'automate_imei_request',
            'flag': app.config['AUTOMATE_IMEI_CHECK']
        },\
        {
            'label': 'overwrite_device_info',
            'flag': app.config['USE_GSMA_DEVICE_INFO']
        }

        documents = {
            'registration': Documents.get_documents('registration'),
            'de_registration': Documents.get_documents('deregistration')
        }

        response = ServerConfigSchema().dump(dict(technologies=technologies,
                                                  documents=documents,
                                                  status_types=status_types,
                                                  device_types=device_types,
                                                  system_config=system_configs)).data

        return Response(json.dumps(response), status=200, mimetype='application/json')
