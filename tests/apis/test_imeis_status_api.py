"""
module for review imei-status-api tests

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
import os
import json

from tests._helpers import create_assigned_dummy_request, create_dummy_devices, create_dummy_request
from app.api.v1.models.approvedimeis import ApprovedImeis

# api urls
IMEIS_STATUS_API = 'api/v1/review/imeis-status'


def test_invalid_input_params(flask_app):
    """Verify that the api responds correctly when invalid input params supplied."""
    # str instead of int in request_id field
    request_id = 'abcd'
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(IMEIS_STATUS_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_id'] == ["Bad 'request_id':'abcd' argument format. Accepts only integer"]

    # int instead of str in request_type field
    request_id = 13123123123132324231312
    request_type = 3
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(IMEIS_STATUS_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_type'] == ["Bad 'request_type':'3' argument format. Accepts only one of ["
                                    "'registration_request', 'de_registration_request']"]

    # str other than registration_request/de-registration_request in request_type field
    request_type = 'abc_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(IMEIS_STATUS_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_type'] == ["Bad 'request_type':'abc_request' argument format. Accepts only one of ["
                                    "'registration_request', 'de_registration_request']"]

    # no request_id argument
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_type={1}'.format(IMEIS_STATUS_API, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_id is required']

    # no request_type argument
    request_id = 1
    rv = flask_app.get('{0}?request_id={1}'.format(IMEIS_STATUS_API, request_id))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_type is required']


def test_request_not_exists(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds correctly when a request_id is given which does not exists in system."""
    # registration_request test
    request_id = 748574387344767294723704
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(IMEIS_STATUS_API, request_id, request_type))
    assert rv.status_code == 204

    # de-registration request test
    request_id = 748574387344767294723704
    request_type = 'de_registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(IMEIS_STATUS_API, request_id, request_type))
    assert rv.status_code == 204


def test_pending_registration_status(flask_app, db, app):
    """Verify that api returns correct imeis count."""
    # registration request
    registration_data = {
        'device_count': 2,
        'imei_per_device': 1,
        'imeis': "[['86834403015010', '868344039012345']]",
        'm_location': 'local',
        'user_name': 'imei stat user 1',
        'user_id': 'imei-stat-user-1'
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
    rv = flask_app.get('{0}?request_id={1}&request_type=registration_request'.format(IMEIS_STATUS_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['not_registered'] == 0
    assert data['pending_registration'] == 2
    assert data['registered'] == 0

    # de-registration request
    de_registration_data = {
        'file': 'de-reg-test-file.txt',
        'device_count': 1,
        'user_id': 'imei-stat-user-2',
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
    approved_imei = ApprovedImeis('35732108234512', 332332, 'whitelist', 'update')
    approved_imei.add()
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(IMEIS_STATUS_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['pending_registration'] == 2
    assert data['not_registered'] == 0
    assert data['registered'] == 0


def test_registered_imeis_count(flask_app, app, db):  # pylint: disable=unused-argument
    """Verify that the api returns correct count of registered imeis of a user."""
    # registration request
    registration_data = {
        'device_count': 3,
        'imei_per_device': 1,
        'imeis': "[['86834403015010', '868344039012345', '868344039000011']]",
        'm_location': 'local',
        'user_name': 'usr-1-01-test-001',
        'user_id': 'usr-1-01-test-001'
    }
    request = create_dummy_request(registration_data, 'Registration', status='Approved')
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
    rv = flask_app.get('{0}?request_id={1}&request_type=registration_request'.format(IMEIS_STATUS_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['pending_registration'] == 0
    assert data['registered'] == 3
    assert data['not_registered'] == 0


def test_duplicated_imeis_count(flask_app, db, app):  # pylint: disable=unused-argument
    """Verify that the system detects duplicate imeis and generated a related file."""
    registration_data = {
        'device_count': 3,
        'imei_per_device': 1,
        'imeis': "[['86800103015010', '8683342039012345', '868000039111111']]",
        'm_location': 'local',
        'user_name': 'usr-2-02-test-002',
        'user_id': 'usr-2-02-test-002'
    }
    request = create_dummy_request(registration_data, 'Registration')
    tracking_id = request.tracking_id
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

    # add an imei to approved imeis
    approved_imei = ApprovedImeis('86800003911111', 332332332, 'whitelist', 'update')
    approved_imei.add()
    rv = flask_app.get('{0}?request_id={1}&request_type=registration_request'.format(IMEIS_STATUS_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['duplicated'] == 1
    duplicated_file_path = '{0}/{1}/duplicated_imeis.txt'.format(app.config['DRS_UPLOADS'], tracking_id)
    assert os.path.exists(duplicated_file_path)

    # read file and check the content
    with open(duplicated_file_path, 'r') as f:
        assert f.readline().split('\n')[0] == '86800003911111'


def test_invalid_imei_count(flask_app, app, db):
    """Verify that the api detects invalid imeis and create an invalid imei file."""
    # de-registration request
    de_registration_data = {
        'file': 'de-reg-test-file.txt',
        'device_count': 1,
        'user_id': 'invalid-imei-stat-user-2',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_dummy_request(de_registration_data, 'De_Registration')
    tracking_id = request.tracking_id
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
        'dereg_id': request.id
    }
    request = create_dummy_devices(device_data, 'De_Registration', request, db, file_content=['357001022345123'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(IMEIS_STATUS_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['invalid'] == 1
    invalid_file_path = '{0}/{1}/invalid_imeis.txt'.format(app.config['DRS_UPLOADS'], tracking_id)
    assert os.path.exists(invalid_file_path)

    # read file and check the content
    with open(invalid_file_path, 'r') as f:
        assert f.readline().split('\n')[0] == '35700102234512'


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed on api."""
    rv = flask_app.post(IMEIS_STATUS_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed on api."""
    rv = flask_app.delete(IMEIS_STATUS_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_put_method_not_allowed(flask_app):
    """Verify that PUT method is not allowed on api."""
    rv = flask_app.put(IMEIS_STATUS_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
