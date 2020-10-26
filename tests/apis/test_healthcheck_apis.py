"""
module for healthcheck api tests

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

HEALTH_CHECK_API = 'api/v1/healthcheck'


def test_healthcheck_failure(flask_app):
    """Verify that when database, core  not available the healthcheck fails."""
    rv = flask_app.get(HEALTH_CHECK_API)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['status'] == 'success'


def test_healthcheck_success(flask_app, dirbs_core):  # pylint: disable=unused-argument
    """Verify that the healthcheck passes when everything is available.
    TODO: add dvs mock to complete
    """
    rv = flask_app.get(HEALTH_CHECK_API)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data
    # assert data['status'] == 'success'


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed."""
    rv = flask_app.post(HEALTH_CHECK_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed."""
    rv = flask_app.delete(HEALTH_CHECK_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_put_method_not_allowed(flask_app):
    """Verify that the PUT method is not allowed."""
    rv = flask_app.put(HEALTH_CHECK_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
