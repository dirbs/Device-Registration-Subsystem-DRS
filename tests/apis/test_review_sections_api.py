"""
module for get sections api tests

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

from tests._helpers import create_assigned_dummy_request
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.deregdetails import DeRegDetails

# api urls
SECTIONS_API = 'api/v1/review/sections'


def test_invalid_input_params(flask_app):
    """Verify that the api responds properly when invalid input params supplied."""
    # str instead of int in request_id field
    request_id = 'abcd'
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(SECTIONS_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_id'] == ["Bad 'request_id':'abcd' argument format. Accepts only integer"]

    # int instead of str in request_type field
    request_id = 13123123123132324231312
    request_type = 3
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(SECTIONS_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_type'] == ["Bad 'request_type':'3' argument format. Accepts only one of ["
                                    "'registration_request', 'de_registration_request']"]

    # str other than registration_request/de-registration_request in request_type field
    request_type = 'abc_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(SECTIONS_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_type'] == ["Bad 'request_type':'abc_request' argument format. Accepts only one of ["
                                    "'registration_request', 'de_registration_request']"]

    # no request_id argument
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_type={1}'.format(SECTIONS_API, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_id is required']

    # no request_type argument
    request_id = 1
    rv = flask_app.get('{0}?request_id={1}'.format(SECTIONS_API, request_id))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_type is required']


def test_request_not_exists(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds correctly when a request_id is given which does not exists in system."""
    # registration_request test
    request_id = 748574387344767294723704
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(SECTIONS_API, request_id, request_type))
    assert rv.status_code == 204

    # de-registration request test
    request_id = 748574387344767294723704
    request_type = 'de_registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(SECTIONS_API, request_id, request_type))
    assert rv.status_code == 204


def test_review_sections_registration(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api returns correct information of sections."""
    # registration request
    data = {
        'device_count': 2,
        'imei_per_device': 1,
        'imeis': "[['86834403015010', '86834403015011']]",
        'm_location': 'local',
        'user_name': 'section rev user 1',
        'user_id': 'section-rev-user-1'
    }
    reviewer_id = 'section-rev-1'
    reviewer_name = 'section rev'
    section = 'device_quota'
    status = 6
    comment = 'this is a test comment'

    request = create_assigned_dummy_request(data, 'Registration', reviewer_id, reviewer_name)
    assert request
    request_id = request.id
    RegDetails.add_comment(section, comment, reviewer_id, reviewer_name, status, request_id)

    rv = flask_app.get('{0}?request_id={1}&request_type=registration_request'.format(SECTIONS_API, request_id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))['sections']
    for sect in data:
        if sect.get('comments'):
            assert sect.get('section_type') == section
            assert sect.get('section_status') == status
            sect_comment = sect.get('comments')[0]
            assert sect_comment.get('user_name') == reviewer_name
            assert sect_comment.get('user_id') == reviewer_id
            assert sect_comment.get('comment') == comment
            assert sect_comment.get('datetime')
        else:
            assert sect.get('section_type') in ['device_description', 'imei_classification',
                                                'imei_registration', 'approval_documents']
            assert sect.get('comments') is None
            assert sect.get('section_status') is None


def test_review_sections_de_registration(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api returns correct information of sections."""
    # de-registration test
    reviewer_id = 'section-rev-1-0'
    reviewer_name = 'section rev0'
    dereg_data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_assigned_dummy_request(dereg_data, 'De-Registration', reviewer_id, reviewer_name)
    assert request
    request_id = request.id
    reviewer_id = 'section-rev-2'
    reviewer_name = 'section rev 2'
    section = 'device_description'
    status = 7
    comment = 'this is a test comment'
    DeRegDetails.add_comment(section, comment, reviewer_id, reviewer_name, status, request_id)

    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(SECTIONS_API, request_id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))['sections']
    for sect in data:
        if sect.get('comments'):
            assert sect.get('section_type') == section
            assert sect.get('section_status') == status
            sect_comment = sect.get('comments')[0]
            assert sect_comment.get('user_name') == reviewer_name
            assert sect_comment.get('user_id') == reviewer_id
            assert sect_comment.get('comment') == comment
            assert sect_comment.get('datetime')
        else:
            assert sect.get('section_type') in ['device_description', 'imei_classification',
                                                'imei_registration', 'approval_documents']
            assert sect.get('comments') is None
            assert sect.get('section_status') is None


def test_empty_sections(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api returns correct info when there is not data in sections table."""
    # registration request
    data = {
        'device_count': 2,
        'imei_per_device': 1,
        'imeis': "[['86834403015010', '86834403015011']]",
        'm_location': 'local',
        'user_name': 'section rev user 1',
        'user_id': 'section-rev-user-1'
    }
    reviewer_id = 'section-rev-1'
    reviewer_name = 'section rev'
    request = create_assigned_dummy_request(data, 'Registration', reviewer_id, reviewer_name)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=registration_request'.format(SECTIONS_API, request_id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))['sections']
    for sect in data:
        assert sect.get('section_type') in ['device_description', 'imei_classification',
                                            'imei_registration', 'approval_documents', 'device_quota']
        assert sect.get('comments') is None
        assert sect.get('section_status') is None

    # de-registration test
    dereg_data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_assigned_dummy_request(dereg_data, 'De-Registration', reviewer_id, reviewer_name)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(SECTIONS_API, request_id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))['sections']
    for sect in data:
        assert sect.get('section_type') in ['device_description', 'imei_classification',
                                            'imei_registration', 'approval_documents']
        assert sect.get('comments') is None
        assert sect.get('section_status') is None


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed on api."""
    rv = flask_app.post(SECTIONS_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed on api."""
    rv = flask_app.delete(SECTIONS_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_put_method_not_allowed(flask_app):
    """Verify that PUT method is not allowed on api."""
    rv = flask_app.put(SECTIONS_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
