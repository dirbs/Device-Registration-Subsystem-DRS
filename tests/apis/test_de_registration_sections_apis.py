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

from tests._helpers import create_dummy_devices, create_dummy_documents, create_dummy_request


DEVICE_DE_REGISTRATION_SECTION_API = 'api/v1/deregistration/sections'
USER_NAME = 'test-abc'
USER_ID = '17102'
REQUEST_DATA = {
    'device_count': 1,
    'user_name': USER_NAME,
    'user_id': USER_ID,
    'reason': 'exporting devices to another country'
}


def test_device_section_method_failed(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration section
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.get('{0}/{1}'.format(DEVICE_DE_REGISTRATION_SECTION_API, 'abc'), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'De-Registration Request not found.'


def test_device_section_method_request(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration section
        method is working properly and response is correct"""
    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['file'] = 'dummy_file'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'New Request')
    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.get('{0}/{1}'.format(DEVICE_DE_REGISTRATION_SECTION_API, de_registration.id), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 200
    assert 'dereg_details' in data
    assert data['dereg_details']
    assert 'status_label' in data['dereg_details']
    assert data['dereg_details']['status_label'] == 'New Request'
    assert 'dereg_device' in data
    assert not data['dereg_device']
    assert 'dereg_docs' in data
    assert not data['dereg_docs']


def test_device_section_method_devices(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration section
        method is working properly and response is correct"""

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['file'] = 'dummy_file.txt'

    de_registration = create_dummy_request(request_data, 'De-Registration', 'Awaiting Documents')
    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.get('{0}/{1}'.format(DEVICE_DE_REGISTRATION_SECTION_API, de_registration.id), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 200
    assert 'dereg_details' in data
    assert data['dereg_details']

    assert 'status_label' in data['dereg_details']
    assert data['dereg_details']['status_label'] == 'Awaiting Documents'

    assert 'dereg_docs' in data
    assert not data['dereg_docs']


def test_device_section_method_documents(flask_app, db, app):
    """ To verify that registration section
        method is working properly and response is correct"""

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'Awaiting Documents')
    headers = {'Content-Type': 'multipart/form-data'}

    documents = [
        {'label': 'shipment document', 'file_name': 'shipment.pdf'},
        {'label': 'authorization document', 'file_name': 'authorize.pdf'},
        {'label': 'certificate document', 'file_name': 'certf.pdf'},
    ]

    device_data = {
        'devices': """[
                    {
                        "tac": "35700102",
                        "model_name": "TA-1034",
                        "brand_name": "NOKIA",
                        "model_num": "TA-1034",
                        "technology": "NONE",
                        "device_type": "Mobile Phone/Feature phone",
                        "count": 2,
                        "operating_system": "N/A"
                    }
                ]""",
        'dereg_id': de_registration.id
    }
    de_registration = create_dummy_devices(device_data, 'De_Registration', de_registration, db,
                                           file_content=['121621090005119'],
                                           file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'],
                                                                          de_registration.tracking_id,
                                                                          request_data['file']))

    registration = create_dummy_documents(documents, 'De-Registration', de_registration, app)
    rv = flask_app.get('{0}/{1}'.format(DEVICE_DE_REGISTRATION_SECTION_API, registration.id), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 200
    assert 'dereg_details' in data
    assert data['dereg_details']

    assert 'status_label' in data['dereg_details']
    assert data['dereg_details']['status_label'] == 'Awaiting Documents'

    assert 'dereg_device' in data
    assert data['dereg_device']

    assert 'tac' in data['dereg_device'][0]
    assert 'model_name' in data['dereg_device'][0]
    assert 'brand_name' in data['dereg_device'][0]
    assert 'model_num' in data['dereg_device'][0]
    assert 'technology' in data['dereg_device'][0]
    assert 'device_type' in data['dereg_device'][0]
    assert 'operating_system' in data['dereg_device'][0]

    assert 'dereg_docs' in data
    assert data['dereg_docs']
