"""
module for common apis test

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
import copy

from tests._helpers import create_dummy_request
from tests.apis.test_de_registration_request_apis import REQUEST_DATA as DE_REG_REQ_DATA


DEVICE_REGISTRATION_RESTART_API = '/api/v1/review/restart/deregistration'


def test_restart_process_closed_request(flask_app, db):  # pylint: disable=unused-argument
    """ unittest for de-registration restart."""

    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request = create_dummy_request(request_data, "De-Registration", 'Closed')
    url = "{0}/{1}".format(DEVICE_REGISTRATION_RESTART_API, request.id)
    rv = flask_app.post(url, data=request_data)

    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    data = json.loads(data)
    assert data['message'] == 'This request cannot be processed'


def test_restart_process_invalid_request(flask_app, db):  # pylint: disable=unused-argument
    """ unittest for de-registration restart."""

    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    create_dummy_request(request_data, "De-Registration", 'New Request')
    url = "{0}/{1}".format(DEVICE_REGISTRATION_RESTART_API, 'abcd')
    rv = flask_app.post(url, data=request_data)

    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'][0] == 'De-Registration Request not found.'
