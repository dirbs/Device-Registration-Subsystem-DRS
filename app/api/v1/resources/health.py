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
import socket
import datetime

from flask import Response
from flask_apispec import marshal_with, doc, MethodResource

from app.api.v1.schema.health import HealthCheckSchema

from app.common.health_checks import database_check, dirbs_core_check


class HealthCheck(MethodResource):
    """Resource class for handling healthcheck api resources."""

    @doc(description='Get health information about the system', tags=['Health'])
    @marshal_with(HealthCheckSchema, code=200, description='On success')
    def get(self):
        """GET method handler."""
        data = []
        for check in [database_check, dirbs_core_check]:
            check_result = check()
            data.append(check_result)
        response = {'results': data}
        response.update(self.calc_status(data))
        return Response(json.dumps(HealthCheckSchema().dump(dict(response)).data),
                        status=200, mimetype='application/json')

    def calc_status(self, data):
        """Method to calculate overall status, hostname and current timestamp."""
        check_status = [check.get('passed') for check in data]
        return {
            'host_name': socket.gethostname(),
            'status': 'success' if all(check_status) else 'failure',
            'time_stamp': datetime.datetime.now()
        }
