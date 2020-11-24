"""
module for common apis test

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
import uuid
import copy

from tests._helpers import create_registration, create_dummy_request

DEVICE_REGISTRATION_REQ_API = 'api/v1/registration'
USER_NAME = 'test-abc'
USER_ID = '17102'
IMEIS = "[['86834403015010']]"
REQUEST_DATA = {

    'device_count': 1,
    'imei_per_device': 1,
    'imeis': IMEIS,
    'm_location': 'local',
    'user_name': USER_NAME,
    'user_id': USER_ID

}


def test_device_post_method(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration post
        method is working properly and response is correct"""
    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=REQUEST_DATA, headers=headers)
    assert rv.status_code == 200

    data = json.loads(rv.data.decode('utf-8'))
    assert data['user_name'] == USER_NAME
    assert data['user_id'] == USER_ID
    assert data['tracking_id'] is not None
    assert data['status_label'] == 'New Request'
    assert data['report_status_label'] == 'New Request'
    assert data['processing_status_label'] == 'New Request'
    assert data['imeis'] == [['86834403015010']]


def test_missing_user_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that request fails incase of
        missing user id"""

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['user_id'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_user_name(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['user_name'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_imeis(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['imeis'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_device_count(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['device_count'] = None

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_zero_device_count(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['device_count'] = 0

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_invalid_device_count(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['device_count'] = -1

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_large_invalid_device_count(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['device_count'] = 100000

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_alphabets_in_device_count(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['device_count'] = 'abcd'

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_imei_per_device(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['imei_per_device'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_zero_imei_per_device(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['imei_per_device'] = 0

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_alphabets_imei_per_device(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['imei_per_device'] = 'abcd'

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_large_invalid_imei_per_device(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['imei_per_device'] = 20000

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_manufacturing_locations(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['m_location'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_integer_value_in_manufacturing_locations(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['m_location'] = 0

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_invalid_string_in_manufacturing_locations(flask_app, db):  # pylint: disable=unused-argument
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['m_location'] = 'abcd'

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_device_get_method(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration get
        method is working properly and response is correct"""
    request = create_registration(REQUEST_DATA, uuid.uuid4())

    api_url = '{api}/{id}'.format(api=DEVICE_REGISTRATION_REQ_API, id=request.id)
    rv = flask_app.get(api_url)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data is not None
    assert data['id'] == request.id


def test_device_put_method_failure(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration put
        method gets failed in case of new request response is correct"""

    request = create_registration(REQUEST_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}
    modified_data = {'m_location': 'overseas', 'reg_id': request.id, 'user_id': USER_ID}
    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=modified_data, headers=headers)
    assert rv.status_code == 422


def test_create_request_file_input_method(flask_app, app, db):  # pylint: disable=unused-argument
    """ unittest for one missing document."""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['device_count'] = 2
    request_data['imei_per_device'] = 3

    request_file = dict()
    file_path = '{0}/{1}'.format('tests/unittest_data/registration', 'request_file.tsv')

    with open(file_path, 'rb') as read_file:
        request_file['file'] = read_file
        request_file['device_count'] = 2
        request_file['imei_per_device'] = 3
        request_file['m_location'] = 'local'
        request_file['user_name'] = 'test-user'
        request_file['user_id'] = '123-test'
        rv = flask_app.post(DEVICE_REGISTRATION_REQ_API, data=request_file, headers=headers)

        assert rv.status_code == 200


def test_device_put_method(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration post
        method is working properly and response is correct"""
    headers = {'Content-Type': 'multipart/form-data'}
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_user_id_update(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that request fails incase of
        missing user id"""
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['user_id'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_user_name_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['user_name'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_imeis_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['imeis'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_device_count_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['device_count'] = None

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_zero_device_count_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['device_count'] = 0

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_invalid_device_count_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['device_count'] = -1

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_large_invalid_device_count_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['device_count'] = 100000

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_alphabets_in_device_count_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['device_count'] = 'abcd'

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_imei_per_device_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['imei_per_device'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_zero_imei_per_device_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['imei_per_device'] = 0

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_alphabets_imei_per_device_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['imei_per_device'] = 'abcd'

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_large_invalid_imei_per_device_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['imei_per_device'] = 20000

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_missing_manufacturing_locations_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['m_location'] = ''

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_integer_value_in_manufacturing_locations_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['m_location'] = 0

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_invalid_string_in_manufacturing_locations_update(flask_app, db):  # pylint: disable=unused-argument
    request = create_dummy_request(REQUEST_DATA, 'Registration', status='New Request')
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = request.id
    request_data['m_location'] = 'abcd'

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_device_get_method_update(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration get
        method is working properly and response is correct"""
    request = create_registration(REQUEST_DATA, uuid.uuid4())

    api_url = '{api}/{id}'.format(api=DEVICE_REGISTRATION_REQ_API, id=request.id)
    rv = flask_app.get(api_url)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data is not None
    assert data['id'] == request.id


def test_device_put_method_failure_update(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration put
        method gets failed in case of new request response is correct"""

    request = create_registration(REQUEST_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}
    modified_data = {'m_location': 'overseas', 'reg_id': request.id, 'user_id': USER_ID}
    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=modified_data, headers=headers)
    assert rv.status_code == 422


def test_device_registration_put_method_close_request(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration put
        method gets failed in case of new request response is correct"""

    request = create_registration(REQUEST_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}
    modified_data = {'close_request': True, 'reg_id': request.id, 'user_id': USER_ID}
    rv = flask_app.put(DEVICE_REGISTRATION_REQ_API, data=modified_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 200
    assert data['status_label'] == 'Closed'
