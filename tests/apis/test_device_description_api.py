"""
module for device-description api tests

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

from tests._helpers import create_assigned_dummy_request, create_dummy_devices

# api urls
DEVICE_DESCRIPTION_API = 'api/v1/review/device-description'


def test_with_invalid_data(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds with correct error messages when invalid input data provided."""
    # str instead of int in request_id field
    request_id = 'abcd'
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(DEVICE_DESCRIPTION_API,
                                                                    request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('request_id') == ["Bad 'request_id':'abcd' argument format. Accepts only integer"]

    # int instead of str in request_type
    request_id = 12312312121212
    request_type = 2
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(DEVICE_DESCRIPTION_API,
                                                                    request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('request_type') == ["Bad 'request_type':'2' argument format. Accepts only one of ["
                                        "'registration_request', 'de_registration_request']"]


def test_request_not_exists(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds properly when a request with given id does not exists in the system."""
    # test for registration request
    request_id = 1223133234232121
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(DEVICE_DESCRIPTION_API,
                                                                    request_id, request_type))
    assert rv.status_code == 204

    # test for de-registration request
    request_type = 'de_registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(DEVICE_DESCRIPTION_API,
                                                                    request_id, request_type))
    assert rv.status_code == 204


def test_single_tac_device_description(flask_app, db, dirbs_core, app):  # pylint: disable=unused-argument
    """Verify that the api responds properly with one tac in devices of a request."""
    # registration request test
    registration_data = {
        'device_count': 1,
        'imei_per_device': 1,
        'imeis': "[['86834403015010']]",
        'm_location': 'local',
        'user_name': 'assign rev user 1',
        'user_id': 'assign-rev-user-1'
    }
    request = create_assigned_dummy_request(registration_data, 'Registration', 'dev-descp-1', 'dev descp')
    device_data = {
        'brand': 'samsung',
        'operating_system': 'android',
        'model_name': 's9',
        'model_num': '30jjd',
        'device_type': 'Smartphone',
        'technologies': '2G,3G,4G',
        'reg_id': request.id
    }
    request = create_dummy_devices(device_data, 'Registration', request)
    rv = flask_app.get('{0}?request_id={1}&request_type=registration_request'.format(
        DEVICE_DESCRIPTION_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data
    assert data.get('gsma_device_description')
    assert data.get('user_device_description')
    user_device_description = data['user_device_description']
    assert user_device_description[0]['model_number'] == '30jjd'
    assert user_device_description[0]['brand'] == 'samsung'
    assert user_device_description[0]['model_name'] == 's9'
    assert user_device_description[0]['device_type'] == 'Smartphone'
    assert user_device_description[0]['operating_system'] == 'android'

    # de registration request
    de_registration_data = {
        'file': 'de-reg-test-file.txt',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_assigned_dummy_request(de_registration_data, 'De_Registration', 'dereg-rev', 'de reg rev')
    device_data = {
        'devices': """[
            {
                "tac": "35732108",
                "model_name": "TA-1034",
                "brand_name": "NOKIA",
                "model_num": "TA-1034",
                "technology": "NONE",
                "device_type": "Mobile Phone/Feature phone",
                "count": 2,
                "operating_system": "N/A"
            }
        ]""",
        'dereg_id': request.id
    }
    request = create_dummy_devices(device_data, 'De_Registration', request, db, file_content=['357321082345123'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(
        DEVICE_DESCRIPTION_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data
    assert data.get('user_device_description')
    assert data.get('gsma_device_description')
    user_device_description = data['user_device_description']
    assert user_device_description[0]['model_number'] == 'TA-1034'
    assert user_device_description[0]['brand'] == 'NOKIA'
    assert user_device_description[0]['model_name'] == 'TA-1034'
    assert user_device_description[0]['device_type'] == 'Mobile Phone/Feature phone'
    assert user_device_description[0]['operating_system'] == 'N/A'


def test_multiple_tac_device_de_registration(flask_app, app, db, dirbs_core):  # pylint: disable=unused-argument
    """Verify that the device description api returns description for multiple devices."""
    # de registration request
    de_registration_data = {
        'file': 'de-reg-test-file.txt',
        'device_count': 1,
        'user_id': 'assign-rev-user-1',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_assigned_dummy_request(de_registration_data, 'De_Registration', 'dereg-rev', 'de reg rev')
    device_data = {
        'devices': """[
                {
                    "tac": "35732108",
                    "model_name": "TA-1034",
                    "brand_name": "NOKIA",
                    "model_num": "TA-1034",
                    "technology": "NONE",
                    "device_type": "Mobile Phone/Feature phone",
                    "count": 2,
                    "operating_system": "N/A"
                },
                {
                    "tac": "35733109",
                    "model_name": "TA-11132",
                    "brand_name": "NOKIA",
                    "model_num": "TA-11132",
                    "technology": "TEC",
                    "device_type": "Smartphone",
                    "count": 1,
                    "operating_system": "Android"
                }
            ]""",
        'dereg_id': request.id
    }
    request = create_dummy_devices(device_data, 'De_Registration', request, db, file_content=['357321082345123'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(
        DEVICE_DESCRIPTION_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data
    assert data.get('user_device_description')
    assert data.get('gsma_device_description')
    assert len(data.get('user_device_description')) == 2
    assert isinstance(data.get('gsma_device_description'), list)


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed."""
    rv = flask_app.post(DEVICE_DESCRIPTION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed."""
    rv = flask_app.delete(DEVICE_DESCRIPTION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_put_method_not_allowed(flask_app):
    """Verify that PUT method is not allowed."""
    rv = flask_app.put(DEVICE_DESCRIPTION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
