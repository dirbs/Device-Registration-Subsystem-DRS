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

from tests._helpers import create_dummy_request, create_dummy_devices
from tests.apis.test_de_registration_request_apis import REQUEST_DATA as DE_REG_REQ_DATA

DE_REGISTRATION_DEVICE_API = 'api/v1/deregistration/devices'
REQUEST_DATA = {
    'devices': [{
        'tac': '12345',
        'model_name': 'Iphone-X',
        'brand_name': 'Apple',
        'model_num': '702-TEST',
        'technology': '3G',
        'device_type': 'Tablet',
        'count': 1,
        'operating_system': 'osx'
    }],
    'dereg_id': 123,
}


def test_device_post_method_de_reg_id_not_found(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that de_registration device
        method is working properly and fails if request not found"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)

    rv = flask_app.post(DE_REGISTRATION_DEVICE_API, data=json.dumps(request_data), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'De-Registration Request not found.'


def test_devices_success(flask_app, app, db):
    """ To verify that de_registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'Awaiting Documents')

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
                                           file_content=['234567898765483'],
                                           file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'],
                                                                          de_registration.tracking_id,
                                                                          request_data['file']))

    rv = flask_app.get("{0}/{1}".format(DE_REGISTRATION_DEVICE_API, de_registration.id),
                        data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 200
    assert 'model_num' in data[0]
    assert 'count' in data[0]
    assert 'brand_name' in data[0]
    assert 'device_type' in data[0]


def test_devices_invalid_status(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that de_registration device fails
        with restricted status"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'

    de_registration = create_dummy_request(request_data, 'De-Registration', 'Awaiting Documents')
    device_data = {'devices': """[{"tac":"35700102","model_name":"TA-1034","brand_name":"NOKIA","model_num":"TA-1034",
    "technology":"NONE","device_type":"Mobile Phone/Feature phone","count":2,"operating_system":"N/A"}]""",
                   'dereg_id': de_registration.id
                   }

    rv = flask_app.post(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'status' in data
    assert data['status'][0] == 'This step can only be performed for New Request'


def test_devices_user_id_missing(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that de_registration device fails
        with missing user ids"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'New Request')
    device_data = {'devices': """[{"tac":"35700102","model_name":"TA-1034","brand_name":"NOKIA","model_num":"TA-1034",
    "technology":"NONE","device_type":"Mobile Phone/Feature phone","count":2,"operating_system":"N/A"}]""",
                   'dereg_id': de_registration.id
                   }

    rv = flask_app.post(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'user_id' in data
    assert data['user_id'][0] == 'User Id is required'


def test_devices_creating_invalid_resp(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that de_registration device fails
        when invalid"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'New Request')

    device_data = {'devices': """[{"tac":"35700102","model_name":"TA-1034","brand_name":"NOKIA","model_num":"TA-1034",
        "technology":"NONE","device_type":"Mobile Phone/Feature phone","count":2,"operating_system":"N/A"}]""",
                   'dereg_id': de_registration.id,
                   'user_id': '17102'
                   }
    rv = flask_app.post(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    # This requires a code change.
    assert rv.status_code == 500
    assert 'message' in data
    assert data['message'][0] == 'Failed to retrieve response, please try later'


def test_devices_creating_missing_model_name(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that de_registration device fails
        when missing model name"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'New Request')

    device_data = {'devices': """[{"tac":"35700102","brand_name":"NOKIA","model_num":"TA-1034","technology":"NONE",
        "device_type":"Mobile Phone/Feature phone","count":2,"operating_system":"N/A"}]""",
                   'dereg_id': de_registration.id,
                   'user_id': '17102'
                   }
    rv = flask_app.post(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'devices' in data
    assert data['devices']['0']['model_name'][0] == 'model_name is a required field'


def test_devices_missing_devices(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that de_registration device fails
        when missing model devices"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    request_data['user_id'] = '17102'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'New Request')

    device_data = {'dereg_id': de_registration.id}
    rv = flask_app.post(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'devices' in data
    assert data['devices'][0] == 'Missing data for required field.'


def test_device_put_method_de_reg_id_not_found(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method fails on invalid request"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(REQUEST_DATA)
    rv = flask_app.post(DE_REGISTRATION_DEVICE_API, data=json.dumps(request_data), headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'De-Registration Request not found.'


def test_update_devices_success(flask_app, app, db):
    """ To verify that registration device
        method is working properly and response is correct"""

    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'Awaiting Documents')
    headers = {'Content-Type': 'multipart/form-data'}

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
                                           file_content=['78788734563219'],
                                           file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'],
                                                                          de_registration.tracking_id,
                                                                          request_data['file']))

    rv = flask_app.get("{0}/{1}".format(DE_REGISTRATION_DEVICE_API, de_registration.id),
                        data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 200
    assert 'model_num' in data[0] and data[0]['model_num'] == "TA-1034"
    assert 'count' in data[0] and data[0]['count'] == 2
    assert 'brand_name' in data[0] and data[0]['brand_name'] == "NOKIA"
    assert 'device_type' in data[0] and data[0]['device_type'] == "Mobile Phone/Feature phone"


def test_devices_update_invalid_status(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'New Request')
    headers = {'Content-Type': 'multipart/form-data'}

    device_data = {'devices': """[{"tac":"35700102","model_name":"TA-1034","brand_name":"NOKIA","model_num":"TA-1034"
    ,"technology":"NONE","device_type":"Mobile Phone/Feature phone","count":2,"operating_system":"N/A"}]""",
                   'dereg_id': de_registration.id
                   }
    rv = flask_app.put(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'status' in data
    assert data['status'][0] == 'Update is restricted for request in status New Request'


def test_devices_update_user_id_missing(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method fails with missing user id"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'Pending Review')

    device_data = {'devices': """[{"tac":"35700102","model_name":"TA-1034","brand_name":"NOKIA","model_num":"TA-1034"
    ,"technology":"NONE","device_type":"Mobile Phone/Feature phone","count":2,"operating_system":"N/A"}]""",
                   'dereg_id': de_registration.id
                   }
    rv = flask_app.put(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'user_id' in data
    assert data['user_id'][0] == 'User Id is required'


def test_devices_update_creating_invalid_resp(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method fails with invalid request"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'Pending Review')
    device_data = {'devices': """[{"tac":"35700102","model_name":"TA-1034","brand_name":"NOKIA","model_num":"TA-1034"
    ,"technology":"NONE","device_type":"Mobile Phone/Feature phone","count":2,"operating_system":"N/A"}]""",
                   'dereg_id': de_registration.id,
                   'user_id': '17102'
                   }
    rv = flask_app.put(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    # requires a code change
    assert rv.status_code == 500
    assert 'message' in data
    assert data['message'][0] == 'Failed to retrieve response, please try later'


def test_devices_update_creating_missing_model_name(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method fails with missing model name"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'Pending Review')

    device_data = {'devices': """[{"tac":"35700102","brand_name":"NOKIA","model_num":"TA-1034","technology":"NONE",
    "device_type":"Mobile Phone/Feature phone","count":2,"operating_system":"N/A"}]""",
                   'dereg_id': de_registration.id,
                   'user_id': '17102'
                   }
    rv = flask_app.put(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'devices' in data
    assert data['devices']['0']['model_name'][0] == 'model_name is a required field'


def test_devices_update_missing_devices(flask_app, app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method fails with missing devices"""

    headers = {'Content-Type': 'multipart/form-data'}
    request_data = copy.deepcopy(DE_REG_REQ_DATA)
    request_data['file'] = 'de-reg-test-file.txt'
    request_data['user_id'] = '17102'
    de_registration = create_dummy_request(request_data, 'De-Registration', 'Pending Review')

    device_data = {'dereg_id': de_registration.id}
    rv = flask_app.put(DE_REGISTRATION_DEVICE_API, data=device_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'devices' in data
    assert data['devices'][0] == 'Missing data for required field.'
