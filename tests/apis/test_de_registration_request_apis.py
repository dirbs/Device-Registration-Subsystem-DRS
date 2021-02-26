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


DEVICE_DE_REGISTRATION_REQ_API = 'api/v1/deregistration'
USER_NAME = 'test-abc'
USER_ID = '17102'
REQUEST_DATA = {
    'device_count': 1,
    'user_name': USER_NAME,
    'user_id': USER_ID,
    'reason': 'exporting devices to another country'

}


def test_request_get(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['device_count'] = 9

    request_file = dict(request_data)
    file_path = '{0}/{1}'.format('tests/unittest_data/de-registration', 'request_file.txt')

    with open(file_path, 'rb') as read_file:
        request_file['file'] = read_file
        rv = flask_app.post(DEVICE_DE_REGISTRATION_REQ_API, data=request_file, headers=headers)

        # code change required
        assert rv.status_code == 500

    rv = flask_app.get(DEVICE_DE_REGISTRATION_REQ_API)
    data = json.loads(rv.data.decode('utf-8'))
    assert data


def test_request_get_single(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    request = create_dummy_request(REQUEST_DATA, 'De-Registration', status='Awaiting Documents')

    rv = flask_app.get("{0}/{1}".format(DEVICE_DE_REGISTRATION_REQ_API, request.id))
    data = json.loads(rv.data.decode('utf-8'))
    assert data
    assert 'report' in data
    assert 'reason' in data
    assert data['status_label'] == 'Awaiting Documents'


def test_invalid_request_get(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""

    rv = flask_app.get("{0}/{1}".format(DEVICE_DE_REGISTRATION_REQ_API, 'abcd'))
    data = json.loads(rv.data.decode('utf-8'))
    data = json.loads(data)
    print(data)
    assert rv.status_code == 200
    assert data['message'] == ['De-Registration Request not found.']


def test_request(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['device_count'] = 9

    request_file = dict(request_data)
    file_path = '{0}/{1}'.format('tests/unittest_data/de-registration', 'request_file.txt')

    with open(file_path, 'rb') as read_file:
        request_file['file'] = read_file
        rv = flask_app.post(DEVICE_DE_REGISTRATION_REQ_API, data=request_file, headers=headers)

        # code change required
        assert rv.status_code == 500


def test_request_file_missing(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['device_count'] = 9

    rv = flask_app.post(DEVICE_DE_REGISTRATION_REQ_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'file' in data
    assert data['file'][0] == 'file is a required field'


def test_request_reason_missing(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data.pop('reason')

    request_file = dict(request_data)
    file_path = '{0}/{1}'.format('tests/unittest_data/de-registration', 'request_file.txt')

    with open(file_path, 'rb') as read_file:
        request_file['file'] = read_file
        rv = flask_app.post(DEVICE_DE_REGISTRATION_REQ_API, data=request_file, headers=headers)
        data = json.loads(rv.data.decode('utf-8'))

        assert rv.status_code == 422
        assert data
        assert 'reason' in data


def test_request_device_count_missing(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data.pop('device_count')

    request_file = dict(request_data)
    file_path = '{0}/{1}'.format('tests/unittest_data/de-registration', 'request_file.txt')

    with open(file_path, 'rb') as read_file:
        request_file['file'] = read_file
        rv = flask_app.post(DEVICE_DE_REGISTRATION_REQ_API, data=request_file, headers=headers)
        data = json.loads(rv.data.decode('utf-8'))

        assert rv.status_code == 422
        assert data
        assert 'device_count' in data


def test_request_update(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['file'] = 'dummy-file.txt'
    request = create_dummy_request(request_data, 'De-Registraiton', 'Pending Review')

    data = {'reason': 'updating the request', 'dereg_id': request.id, 'user_id': USER_ID}
    rv = flask_app.put(DEVICE_DE_REGISTRATION_REQ_API,
                       data=data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 200
    assert 'user_id' in data
    assert 'reason' in data
    assert 'file' in data


def test_request_file_update(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['file'] = 'dummy-file.txt'
    request = create_dummy_request(request_data, 'De-Registraiton', 'Pending Review')

    request_data['device_count'] = 9
    request_data['dereg_id'] = request.id

    request_file = dict(request_data)
    file_path = '{0}/{1}'.format('tests/unittest_data/de-registration', 'request_file.txt')

    with open(file_path, 'rb') as read_file:
        request_file['file'] = read_file
        rv = flask_app.put(DEVICE_DE_REGISTRATION_REQ_API, data=request_file, headers=headers)

        # code change required
        assert rv.status_code == 500


def test_request_file_update_invalid_device(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['file'] = 'dummy-file.txt'
    request = create_dummy_request(request_data, 'De-Registraiton', 'New Request')

    request_data['device_count'] = 90
    request_data['dereg_id'] = request.id

    request_file = dict(request_data)
    file_path = '{0}/{1}'.format('tests/unittest_data/de-registration', 'request_file.txt')

    with open(file_path, 'rb') as read_file:
        request_file['file'] = read_file
        rv = flask_app.put(DEVICE_DE_REGISTRATION_REQ_API, data=request_file, headers=headers)
        data = json.loads(rv.data.decode('utf-8'))
        assert rv.status_code == 422
        assert data['status'][0] == 'The request status is New Request, which cannot be updated'


def test_request_update_failed(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['file'] = 'dummy-file.txt'
    request = create_dummy_request(request_data, 'De-Registraiton', 'New Request')

    data = {'reason': 'updating the request', 'dereg_id': request.id, 'user_id': USER_ID}
    rv = flask_app.put(DEVICE_DE_REGISTRATION_REQ_API,
                       data=data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'reason' in data
    assert data['reason'][0] == 'The request status is New Request, which cannot be updated'


def test_request_closed(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """ unittest for de-registration request"""
    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['file'] = 'dummy-file.txt'
    request = create_dummy_request(request_data, 'De-Registraiton', 'New Request')

    data = {'close_request': True, 'dereg_id': request.id, 'user_id': USER_ID}
    rv = flask_app.put(DEVICE_DE_REGISTRATION_REQ_API,
                       data=data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 200
    assert data['status_label'] == 'Closed'
