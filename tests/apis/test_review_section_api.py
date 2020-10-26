"""
module for review-sections api tests

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

from tests._helpers import create_assigned_dummy_request, create_dummy_request

# api urls
REVIEW_SECTION_API = 'api/v1/review/review-section'


def test_invalid_input_params(flask_app):
    """Verify that the api should respond properly when invalid input params supplied."""
    headers = {'Content-Type': 'application/json'}

    # int instead of str in section field
    body_data = {'section': 2, 'status': 6, 'request_type': 'registration_request',
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['section'] == ["Bad 'section':'2' argument format. Accepts only one of "
                                                              "['device_quota', 'device_description', "
                                                              "'imei_classification', 'imei_registration', "
                                                              "'approval_documents']"]

    # other str instead of required str in section field
    body_data = {'section': 'abcd', 'status': 6, 'request_type': 'registration_request',
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['section'] == ["Bad 'section':'abcd' argument format. Accepts only one "
                                                              "of ['device_quota', 'device_description', "
                                                              "'imei_classification', 'imei_registration', "
                                                              "'approval_documents']"]

    # str instead of int in status field
    body_data = {'section': 'device_quota', 'status': 'a', 'request_type': 'registration_request',
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['status'] == ["Bad 'status':'a' argument format. Accepts only integer"]

    # status other than 5, 6, 7 in status field
    body_data = {'section': 'device_quota', 'status': 10, 'request_type': 'registration_request',
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['section_status must be Information Requested, Approved '
                                                            'or Rejected']

    # int instead of str in request_type
    body_data = {'section': 'device_quota', 'status': 5, 'request_type': 1,
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['request_type'] == ["Bad 'request_type':'1' argument format. Accepts "
                                                                   "only one of ['registration_request', "
                                                                   "'de_registration_request']"]

    # other str instead of registration_request/de_registration_request in request_type
    body_data = {'section': 'device_quota', 'status': 5, 'request_type': 'abcd',
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['request_type'] == ["Bad 'request_type':'abcd' argument format. Accepts "
                                                                   "only one of ['registration_request', "
                                                                   "'de_registration_request']"]

    # str instead of int in request_id
    body_data = {'section': 'device_quota', 'status': 5, 'request_type': 'registration_request',
                 'request_id': 'abcd', 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['request_id'] == ["Bad 'request_id':'abcd' argument format. Accepts "
                                                                 "only integer"]

    # int instead of str in comment
    body_data = {'section': 'device_quota', 'status': 5, 'request_type': 'registration_request',
                 'request_id': 56, 'comment': 1233, 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['comment'] == ["Bad 'comment':'1233' argument format."]

    # int instead of str in reviewer_name
    body_data = {'section': 'device_quota', 'status': 5, 'request_type': 'registration_request',
                 'request_id': 56, 'comment': '1233', 'reviewer_name': 1,
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['reviewer_name'] == ["Bad 'reviewer_name':'1' argument format."]

    # int instead of str in reviewer_id
    body_data = {'section': 'device_quota', 'status': 5, 'request_type': 'registration_request',
                 'request_id': 56, 'comment': '1233', 'reviewer_name': 'rev1',
                 'reviewer_id': 1}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['reviewer_id'] == ["Bad 'reviewer_id':'1' argument format."]


def test_null_input_params(flask_app):
    """Verify that the api responds properly when input arguments are null."""
    headers = {'Content-Type': 'application/json'}

    # no section argument
    body_data = {'status': 6, 'request_type': 'registration_request',
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['section is required']

    # no status argument
    body_data = {'section': 'device_quota', 'request_type': 'registration_request',
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['status is required']

    # no request_type argument
    body_data = {'section': 'device_quota', 'status': 5,
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['request_type is required']

    # no request_id argument
    body_data = {'section': 'device_quota', 'status': 5, 'request_type': 'registration_request',
                 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['request_id is required']

    # no reviewer_name argument
    body_data = {'section': 'device_quota', 'status': 5, 'request_type': 'registration_request',
                 'request_id': 56, 'comment': '1233',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['reviewer_name is required']

    # no reviewer_id argument
    body_data = {'section': 'device_quota', 'status': 5, 'request_type': 'registration_request',
                 'request_id': 56, 'comment': '1233', 'reviewer_name': '1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['reviewer_id is required']


def test_request_not_exists(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds correctly when no request exists in system."""
    headers = {'Content-Type': 'application/json'}

    # registration request
    body_data = {'section': 'device_quota', 'status': 6, 'request_type': 'registration_request',
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 204

    # de registration request
    body_data = {'section': 'device_quota', 'status': 6, 'request_type': 'de_registration_request',
                 'request_id': 12312313234234231231313, 'comment': 'this is a test comment', 'reviewer_name': 'rev1',
                 'reviewer_id': 'rev1'}
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 204


def test_review_section_status_param(flask_app):
    """Verify that the status param should be in 5,6,7 and api responds accordingly."""
    headers = {'Content-Type': 'application/json'}
    for status in [1, 2, 4, 10, 15, 9, 8]:
        body_data = {'section': 'device_quota', 'status': status, 'request_type': 'registration_request',
                     'request_id': 12312313234234231231313, 'comment': 'this is a test comment',
                     'reviewer_name': 'rev1',
                     'reviewer_id': 'rev1'}
        rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body_data), headers=headers)
        assert rv.status_code == 422
        data = json.loads(rv.data.decode('utf-8'))
        assert data['error'] == ['section_status must be Information Requested, Approved or Rejected']


def test_review_section(flask_app, db):  # pylint: disable=unused-argument
    """Verify that if a request is in review already than a section of it can be reviewed."""
    headers = {'Content-Type': 'application/json'}

    # registration request
    reviewer_id = 'section-rev-1'
    reviewer_name = 'section rev'
    data = {
        'device_count': 2,
        'imei_per_device': 1,
        'imeis': "[['86834403015010', '86834403015011']]",
        'm_location': 'local',
        'user_name': 'section rev user 1',
        'user_id': 'section-rev-user-1'
    }
    request = create_assigned_dummy_request(data, 'Registration', reviewer_id, reviewer_name)
    assert request
    request_id = request.id

    # making api call
    body = {
        'section': 'device_quota',
        'request_type': 'registration_request',
        'status': 6,
        'request_id': request_id,
        'comment': 'this is a test comment',
        'reviewer_id': reviewer_id,
        'reviewer_name': reviewer_name
    }
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body), headers=headers)
    assert rv.status_code == 201
    assert json.loads(rv.data.decode('utf-8'))['message'] == 'Comment on request added successfully'

    # test with invalid reviewer_id
    body['reviewer_id'] = 'abc-rev1'
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body), headers=headers)
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['invalid reviewer abc-rev1']

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
    body['request_type'] = 'de_registration_request'
    body['request_id'] = request_id
    body['reviewer_id'] = reviewer_id
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body), headers=headers)
    assert rv.status_code == 201
    assert json.loads(rv.data.decode('utf-8'))['message'] == 'Comment on request added successfully'

    # test with invalid reviewer
    body['reviewer_id'] = 'test-abc'
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body), headers=headers)
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['invalid reviewer test-abc']


def test_pending_review_request(flask_app, db):  # pylint: disable=unused-argument
    """Verify that a pending request sections can not be reviewed."""
    headers = {'Content-Type': 'application/json'}

    # registration request
    reviewer_id = 'section-rev-1'
    reviewer_name = 'section rev'
    data = {
        'device_count': 2,
        'imei_per_device': 1,
        'imeis': "[['86834403015010', '86834403015011']]",
        'm_location': 'local',
        'user_name': 'section rev user 1',
        'user_id': 'section-rev-user-1'
    }
    request = create_dummy_request(data, 'Registration')
    assert request
    request_id = request.id

    # make api call
    body = {
        'section': 'device_quota',
        'request_type': 'registration_request',
        'status': 6,
        'request_id': request_id,
        'comment': 'this is a test comment',
        'reviewer_id': reviewer_id,
        'reviewer_name': reviewer_name
    }
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body), headers=headers)
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['request {0} should be in-review'.format(request_id)]

    # de-registration test
    data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_dummy_request(data, 'De-Registration')
    assert request
    request_id = request.id

    # make api call
    body['request_type'] = 'de_registration_request'
    body['request_id'] = request_id
    body['reviewer_id'] = reviewer_id
    rv = flask_app.put(REVIEW_SECTION_API, data=json.dumps(body), headers=headers)
    assert rv.status_code == 400
    assert json.loads(rv.data.decode('utf-8'))['error'] == ['request {0} should be in-review'.format(request_id)]


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed on api."""
    rv = flask_app.post(REVIEW_SECTION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed on api."""
    rv = flask_app.delete(REVIEW_SECTION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_get_method_not_allowed(flask_app):
    """Verify that GET method is not allowed on api."""
    rv = flask_app.get(REVIEW_SECTION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
