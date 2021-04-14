"""
module for assign-reviewer api test

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

from tests._helpers import create_dummy_request

# api urls
ASSIGN_REVIEWER_API = 'api/v1/review/assign-reviewer'


def test_with_invalid_params(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds with proper error messages when invalid params supplied."""
    # str instead of int in request_id
    headers = {'Content-Type': 'application/json'}
    body_data = {
        'request_id': 'abcd',
        'request_type': 'registration_request',
        'reviewer_id': 'string',
        'reviewer_name': 'string'
    }
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('request_id') == ["Bad 'request_id':'abcd' argument format. Accepts only integer"]

    # other str instead of 'registration_request' or 'de_registration_request' in request_type
    body_data = {
        'request_id': 1,
        'request_type': 'abcd',
        'reviewer_id': 'string',
        'reviewer_name': 'string'
    }
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('request_type') == ["Bad 'request_type':'abcd' argument format. Accepts only one of ["
                                        "'registration_request', 'de_registration_request']"]

    # int instead of str in reviewer_id
    body_data = {
        'request_id': 1,
        'request_type': 'registration_request',
        'reviewer_id': 1223,
        'reviewer_name': 'string'
    }
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('reviewer_id') == ["Bad 'reviewer_id':'1223' argument format."]

    # int instead of str in reviewer_name
    body_data = {
        'request_id': 1,
        'request_type': 'registration_request',
        'reviewer_id': 'string',
        'reviewer_name': 23234
    }
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('reviewer_name') == ["Bad 'reviewer_name':'23234' argument format."]


def test_null_params(flask_app):
    """Verify that the api responds properly when null params are supplied."""
    # no request_id param
    headers = {'Content-Type': 'application/json'}
    body_data = {
        'request_type': 'registration_request',
        'reviewer_id': 'string',
        'reviewer_name': 'string'
    }
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_id is required']

    # no request_type param
    body_data.update({'request_id': 5667})
    del body_data['request_type']
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_type is required']

    # no reviewer_id
    body_data.update({'request_type': 'registration_request'})
    del body_data['reviewer_id']
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['reviewer_id is required']

    # no reviewer_name
    body_data.update({'reviewer_id': 'dgggd'})
    del body_data['reviewer_name']
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['reviewer_name is required']


def test_request_not_exists(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds with correct message if the request for which
    id is given does not exists in the system.
    """
    # test for registration request
    headers = {'Content-Type': 'application/json'}
    body_data = {
        'request_id': 1234567890123,
        'request_type': 'registration_request',
        'reviewer_id': 'test-reviewer',
        'reviewer_name': 'test_reviewer'
    }
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 204

    # test for de-registration request
    body_data['request_type'] = 'de_registration_request'
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 204


def test_assign_reviewer(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the assign reviewer api assigns a reviewer to a
    request in pending review status.
    """
    headers = {'Content-Type': 'application/json'}
    data = {
        'device_count': 1,
        'imei_per_device': 1,
        'imeis': "[['86834403015010']]",
        'm_location': 'local',
        'user_name': 'assign rev user 1',
        'user_id': 'assign-rev-user-1'
    }

    # registration request test, creating dummy request
    request = create_dummy_request(data, 'Registration')
    assert request
    request_id = request.id

    # make api request
    reviewer_id = 'assign-rev-1'
    request_data = {
        'request_id': request_id,
        'reviewer_id': reviewer_id,
        'reviewer_name': 'assign rev',
        'request_type': 'registration_request'
    }
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 201
    rv_data = json.loads(rv.data.decode('utf-8'))
    assert rv_data['message'] == 'reviewer {0} assigned to request {1}'.format(reviewer_id, request_id)

    # de-registration request test, creating dummy request
    data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_dummy_request(data, 'De-Registration')
    request_id = request.id

    # make api call
    request_data['request_id'] = request_id
    request_data['request_type'] = 'de_registration_request'
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 201
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == 'reviewer {0} assigned to request {1}'.format(reviewer_id, request_id)


def test_incomplete_request(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api do not assign an incomplete request and respond accordingly."""
    # registration request
    headers = {'Content-Type': 'application/json'}
    data = {
        'device_count': 1,
        'imei_per_device': 1,
        'imeis': "[['86834403015010']]",
        'm_location': 'local',
        'user_name': 'assign rev user 1',
        'user_id': 'assign-rev-user-1'
    }
    request = create_dummy_request(data, 'Registration', 'In Review')
    assert request
    request_id = request.id

    # make api call
    reviewer_id = 'assign-rev-1'
    request_data = {
        'request_id': request_id,
        'reviewer_id': reviewer_id,
        'reviewer_name': 'assign rev',
        'request_type': 'registration_request'
    }
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 400
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['incomplete request {0} can not be assigned/reviewed'.format(request_id)]

    # de registration test
    data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_dummy_request(data, 'De-Registration', 'In Review')
    request_id = request.id

    # make api call
    request_data['request_id'] = request_id
    request_data['request_type'] = 'de_registration_request'
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 400
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['incomplete request {0} can not be assigned/reviewed'.format(request_id)]


def test_already_assigned_request(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api do not reassign an already assigned request and respond accordingly."""
    # make dummy registration request, assign it and then try to reassign it
    headers = {'Content-Type': 'application/json'}
    data = {
        'device_count': 1,
        'imei_per_device': 1,
        'imeis': "[['86834403015010']]",
        'm_location': 'local',
        'user_name': 'assign rev user 1',
        'user_id': 'assign-rev-user-1'
    }

    # registration request test, creating dummy request
    request = create_dummy_request(data, 'Registration')
    assert request
    request_id = request.id

    # make api request
    reviewer_id = 'assign-rev-1'
    request_data = {
        'request_id': request_id,
        'reviewer_id': reviewer_id,
        'reviewer_name': 'assign rev',
        'request_type': 'registration_request'
    }
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 201

    # try to reassign
    request_data['reviewer_id'] = 'reassign-rev-1'
    request_data['reviewer_name'] = 'reassign rev'
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 400

    # de-registration test
    data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_dummy_request(data, 'De-Registration')
    request_id = request.id

    # make api call
    request_data['request_id'] = request_id
    request_data['request_type'] = 'de_registration_request'
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 201

    # try to reassign
    request_data['reviewer_id'] = 'rev-2'
    request_data['reviewer_name'] = 'rev2'
    rv = flask_app.put(ASSIGN_REVIEWER_API, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 400


def test_get_method_not_allowed(flask_app):
    """Verify that GET method is not allowed."""
    rv = flask_app.get(ASSIGN_REVIEWER_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed."""
    rv = flask_app.delete(ASSIGN_REVIEWER_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed."""
    rv = flask_app.post(ASSIGN_REVIEWER_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
