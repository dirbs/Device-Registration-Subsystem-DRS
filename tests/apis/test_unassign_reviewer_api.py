"""
module for review unassign-reviewer api tests

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

from tests._helpers import create_assigned_dummy_request

# api urls
UNASSIGN_REVIEWER_API = 'api/v1/review/unassign-reviewer'


def test_invalid_input_params(flask_app):
    """Verify that api responds properly when invalid input supplied."""
    # str instead of int in request_id field
    headers = {'Content-Type': 'application/json'}
    body_data = {
        'request_id': 'abcd',
        'request_type': 'registration_request',
        'reviewer_id': 'rev1'
    }
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_id'] == ["Bad 'request_id':'abcd' argument format. Accepts only integer"]

    # int instead of str in request_type
    body_data['request_id'] = 1
    body_data['request_type'] = 2
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_type'] == ["Bad 'request_type':'2' argument format. Accepts only one of ["
                                    "'registration_request', 'de_registration_request']"]

    # other str than registration_request/de_registration_request in request_type
    body_data['request_type'] = 'abcd'
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_type'] == ["Bad 'request_type':'abcd' argument format. Accepts only one of ["
                                    "'registration_request', 'de_registration_request']"]

    # int instead of str in reviewer_id
    body_data['request_type'] = 'registration_request'
    body_data['reviewer_id'] = 1
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['reviewer_id'] == ["Bad 'reviewer_id':'1' argument format."]


def test_null_input_params(flask_app):
    """Verify that the api returns proper error response when no params are given."""
    headers = {'Content-Type': 'application/json'}

    # no request id argument
    body_data = {
        'request_type': 'registration_request',
        'reviewer_id': 'rev1'
    }
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ["request_id is required"]

    # no request_type argument
    body_data['request_id'] = 1
    del body_data['request_type']
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ["request_type is required"]

    # no reviewer_id argument
    body_data['request_type'] = 'registration_request'
    del body_data['reviewer_id']
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ["reviewer_id is required"]


def test_request_not_exists(flask_app, db):  # pylint: disable=unused-argument
    """Verify that api responds for request which does not exists in system."""
    # registration_request test
    headers = {'Content-Type': 'application/json'}
    body_data = {
        'request_id': 37284234802304802384,
        'request_type': 'registration_request',
        'reviewer_id': 'rev1'
    }
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 204

    # de registration request
    body_data['request_type'] = 'de_registration_request'
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 204


def test_un_assign_request(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api successfully un-assign a user from a request."""
    # registration test
    headers = {'Content-Type': 'application/json'}
    data = {
        'device_count': 1,
        'imei_per_device': 1,
        'imeis': "[['86834403015010']]",
        'm_location': 'local',
        'user_name': 'assign rev user 1',
        'user_id': 'assign-rev-user-1'
    }
    reviewer_id = 'unassign-rev-1'
    reviewer_name = 'unassign rev'
    request = create_assigned_dummy_request(data, 'Registration', reviewer_id, reviewer_name)
    assert request
    request_id = request.id

    # make api call
    request_data = {
        'request_id': request_id,
        'reviewer_id': reviewer_id,
        'request_type': 'registration_request'
    }
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 201
    response_data = json.loads(rv.data.decode('utf-8'))
    assert response_data['message'] == 'Successfully un-assigned the request'

    # de-registration test
    data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_assigned_dummy_request(data, 'De-Registration', reviewer_id, reviewer_name)
    assert request
    request_id = request.id

    # make api call
    request_data['request_id'] = request_id
    request_data['request_type'] = 'de_registration_request'
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 201
    response_data = json.loads(rv.data.decode('utf-8'))
    assert response_data['message'] == 'Successfully un-assigned the request'


def test_invalid_reviewer(flask_app, db):  # pylint: disable=unused-argument
    """Verify that only assigned reviewer can un-assign the request and api responds
    accordingly.
    """
    # registration test
    headers = {'Content-Type': 'application/json'}
    data = {
        'device_count': 1,
        'imei_per_device': 1,
        'imeis': "[['86834403015010']]",
        'm_location': 'local',
        'user_name': 'assign rev user 1',
        'user_id': 'assign-rev-user-1'
    }
    reviewer_id = 'unassign-rev-1'
    reviewer_name = 'unassign rev'
    request = create_assigned_dummy_request(data, 'Registration', reviewer_id, reviewer_name)
    assert request
    request_id = request.id

    # make api call
    request_data = {
        'request_id': request_id,
        'reviewer_id': 'abc-rev',
        'request_type': 'registration_request'
    }
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 400
    response_data = json.loads(rv.data.decode('utf-8'))
    assert response_data['error'] == ['invalid reviewer abc-rev']

    # de-registration test
    data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_assigned_dummy_request(data, 'De-Registration', reviewer_id, reviewer_name)
    assert request
    request_id = request.id

    # make api call
    request_data['request_id'] = request_id
    request_data['request_type'] = 'de_registration_request'
    request_data['reviewer_id'] = 'abc-rev'
    rv = flask_app.put(UNASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 400
    response_data = json.loads(rv.data.decode('utf-8'))
    assert response_data['error'] == ['invalid reviewer abc-rev']


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed on api."""
    rv = flask_app.post(UNASSIGN_REVIEWER_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed on api."""
    rv = flask_app.delete(UNASSIGN_REVIEWER_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_get_method_not_allowed(flask_app):
    """Verify that PUT method is not allowed on api."""
    rv = flask_app.get(UNASSIGN_REVIEWER_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
