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
import uuid

from tests._helpers import create_registration, create_dummy_devices, create_dummy_documents


DEVICE_REGISTRATION_SECTION_API = 'api/v1/registration/sections'
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


def test_device_section_method_failed(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration section
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.get('{0}/{1}'.format(DEVICE_REGISTRATION_SECTION_API, 'abc'), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'Registration Request not found.'


def test_device_section_method_request(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration section
        method is working properly and response is correct"""

    registration = create_registration(REQUEST_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.get('{0}/{1}'.format(DEVICE_REGISTRATION_SECTION_API, registration.id), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 200
    assert 'reg_details' in data
    assert data
    assert 'status_label' in data['reg_details']
    assert data['reg_details']['status_label'] == 'New Request'

    assert 'reg_device' in data
    assert not data['reg_docs']
    assert not data['reg_docs']


def test_device_section_method_devices(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration section
        method is working properly and response is correct"""

    registration = create_registration(REQUEST_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    device_data = {
        'brand': 'samsung',
        'operating_system': 'android',
        'model_name': 's9',
        'model_num': '30jjd',
        'device_type': 'Smartphone',
        'technologies': '2G,3G,4G',
        'reg_id': registration.id
    }

    registration = create_dummy_devices(device_data, 'Registration', registration)
    rv = flask_app.get('{0}/{1}'.format(DEVICE_REGISTRATION_SECTION_API, registration.id), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 200
    assert 'reg_details' in data
    assert data['reg_details']
    assert 'status_label' in data['reg_details']
    assert data['reg_details']['status_label'] == 'New Request'

    assert 'reg_device' in data
    assert data['reg_device']
    assert 'model_num' in data['reg_device']
    assert 'technologies' in data['reg_device']

    assert 'reg_docs' in data
    assert not data['reg_docs']


def test_device_section_method_documents(flask_app, db, app):  # pylint: disable=unused-argument
    """ To verify that registration section
        method is working properly and response is correct"""

    registration = create_registration(REQUEST_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    device_data = {
        'brand': 'samsung',
        'operating_system': 'android',
        'model_name': 's9',
        'model_num': '30jjd',
        'device_type': 'Smartphone',
        'technologies': '2G,3G,4G',
        'reg_id': registration.id
    }

    documents = [
        {'label': 'shipment document', 'file_name': 'shipment.pdf'},
        {'label': 'authorization document', 'file_name': 'authorize.pdf'},
        {'label': 'certificate document', 'file_name': 'certf.pdf'},
    ]

    registration = create_dummy_devices(device_data, 'Registration', registration)
    registration = create_dummy_documents(documents, 'Registration', registration, app)
    rv = flask_app.get('{0}/{1}'.format(DEVICE_REGISTRATION_SECTION_API, registration.id), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 200
    assert 'reg_details' in data
    assert data['reg_details']
    assert 'status_label' in data['reg_details']
    assert data['reg_details']['status_label'] == 'New Request'

    assert 'reg_device' in data
    assert data['reg_device']
    assert 'model_num' in data['reg_device']
    assert 'technologies' in data['reg_device']

    assert 'reg_docs' in data
    assert len(data['reg_docs']) == 3
