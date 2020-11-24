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

from tests._helpers import create_de_registration, create_dummy_request
from tests.apis.test_de_registration_request_apis import REQUEST_DATA as DE_REG_REQ_DATA


DEVICE_REGISTRATION_DOC_API = 'api/v1/deregistration/documents'
USER_NAME = 'test-abc'
USER_ID = '17102'
REQUEST_DATA = {
    'user_id': USER_ID
}
DOC_NAMES = ['authorization document', 'certificate document', 'shipment document']


def test_documents_invalid_status(flask_app, db):  # pylint: disable=unused-argument
    """ unittest for registration documents."""
    headers = {'Content-Type': 'multipart/form-data'}
    request = create_de_registration(DE_REG_REQ_DATA, uuid.uuid4())

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['dereg_id'] = request.id

    rv = flask_app.post(DEVICE_REGISTRATION_DOC_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'status' in data
    assert data['status'][0] == 'This step can only be performed for request with Awaiting Document status'


def test_required_documents_all_missing(flask_app, db):  # pylint: disable=unused-argument
    """ unittest for registration documents all missing"""
    headers = {'Content-Type': 'multipart/form-data'}
    request = create_dummy_request(DE_REG_REQ_DATA, 'De-Registration', status='Awaiting Documents')

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['dereg_id'] = request.id

    rv = flask_app.post(DEVICE_REGISTRATION_DOC_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'authorization document' in data
    assert 'certificate document' in data
    assert 'shipment document' in data
    assert data['authorization document'][0] == 'This is a required Document'
    assert data['certificate document'][0] == 'This is a required Document'
    assert data['shipment document'][0] == 'This is a required Document'


def test_required_documents_missing_docs(flask_app, app, db):  # pylint: disable=unused-argument
    """ unittest for one missing document."""
    headers = {'Content-Type': 'multipart/form-data'}
    request = create_dummy_request(DE_REG_REQ_DATA, 'De-Registration', status='Awaiting Documents')
    document_obj = dict()
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['dereg_id'] = request.id

    file_path = '{0}/{1}'.format('tests/unittest_data', 'shipment.pdf')

    with open(file_path, 'rb') as read_file:
        document_obj['shipment document'] = read_file
        document_obj['dereg_id'] = request.id
        rv = flask_app.post(DEVICE_REGISTRATION_DOC_API, data=document_obj, headers=headers)
        data = json.loads(rv.data.decode('utf-8'))

        assert rv.status_code == 422
        assert 'authorization document' in data
        assert 'certificate document' in data
        assert data['authorization document'][0] == 'This is a required Document'
        assert data['certificate document'][0] == 'This is a required Document'


def test_required_documents_invalid_extension(flask_app, app, db):  # pylint: disable=unused-argument
    """ unittest for one missing document."""
    headers = {'Content-Type': 'multipart/form-data'}
    request = create_dummy_request(DE_REG_REQ_DATA, 'De-Registration', status='Awaiting Documents')
    document_obj = dict()
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['dereg_id'] = request.id

    file_path = '{0}/{1}'.format('tests/unittest_data/registration', 'request_file.tsv')

    with open(file_path, 'rb') as read_file:
        document_obj['shipment document'] = read_file
        document_obj['dereg_id'] = request.id
        rv = flask_app.post(DEVICE_REGISTRATION_DOC_API, data=document_obj, headers=headers)
        data = json.loads(rv.data.decode('utf-8'))
        assert rv.status_code == 422
        assert 'document_format' in data
        assert data['document_format'][0] == 'File format tsv is not allowed'


def test_required_documents_update_missing_user(flask_app, app, db):  # pylint: disable=unused-argument
    """ unittest for one missing document."""
    headers = {'Content-Type': 'multipart/form-data'}
    request = create_dummy_request(DE_REG_REQ_DATA, 'De-Registration', status='Awaiting Documents')
    document_obj = dict()
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['dereg_id'] = request.id

    file_path = '{0}/{1}'.format('tests/unittest_data', 'shipment.pdf')

    with open(file_path, 'rb') as read_file:
        document_obj['shipment document'] = read_file
        document_obj['dereg_id'] = request.id
        rv = flask_app.put(DEVICE_REGISTRATION_DOC_API, data=document_obj, headers=headers)
        data = json.loads(rv.data.decode('utf-8'))
        assert rv.status_code == 422
        assert 'user_id' in data
        assert data['user_id'][0] == 'User Id is required'


def test_required_documents_update_invalid_extension(flask_app, app, db):  # pylint: disable=unused-argument
    """ unittest for one missing document."""
    headers = {'Content-Type': 'multipart/form-data'}
    request = create_dummy_request(DE_REG_REQ_DATA, 'De-Registration', status='Awaiting Documents')
    document_obj = dict()
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['dereg_id'] = request.id

    file_path = '{0}/{1}'.format('tests/unittest_data/registration', 'request_file.tsv')

    with open(file_path, 'rb') as read_file:
        document_obj['shipment document'] = read_file
        document_obj['dereg_id'] = request.id
        rv = flask_app.put(DEVICE_REGISTRATION_DOC_API, data=document_obj, headers=headers)
        data = json.loads(rv.data.decode('utf-8'))
        assert rv.status_code == 422
        assert 'document_format' in data
        assert data['document_format'][0] == 'File format tsv is not allowed'


def test_documents_get_empty_list(flask_app, db):  # pylint: disable=unused-argument
    """ unittest for registration documents all missing"""
    request = create_dummy_request(DE_REG_REQ_DATA, 'De-Registration', status='Awaiting Documents')

    rv = flask_app.get("{0}/{1}".format(DEVICE_REGISTRATION_DOC_API, request.id))
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 200
    assert not data


def test_documents_get_invalid_request(flask_app, db):  # pylint: disable=unused-argument
    """ unittest for registration documents all missing"""

    rv = flask_app.get("{0}/{1}".format(DEVICE_REGISTRATION_DOC_API, '123'))
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == "De-Registration Request not found."
