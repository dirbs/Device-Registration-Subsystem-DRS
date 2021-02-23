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
import copy

from tests._helpers import create_registration
from tests.apis.test_registration_request_apis import REQUEST_DATA as REG_REQ_DATA


DEVICE_REGISTRATION_API = 'api/v1/registration/device'
USER_ID = '17102'
USER_NAME = 'test-abc'
IMEIS = "[['86834403015010']]"
REG_ID = 12345
BRAND = 'Apple'
OPERATING_SYSTEM = 'osx'
MODEL_NAME = 'Iphone-X'
MODEL_NUMBER = '702-TEST'
DEVICE_TYPE = 'Tablet'
TECHNOLOGIES = '3G'

REQUEST_DATA = {
    'user_id': USER_ID,
    'reg_id': REG_ID,
    'brand': BRAND,
    'operating_system': OPERATING_SYSTEM,
    'model_name': MODEL_NAME,
    'model_num': MODEL_NUMBER,
    'device_type': DEVICE_TYPE,
    'technologies': TECHNOLOGIES
}

# TODO: DOC strings


def test_device_post_method_reg_id_not_found(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=REQUEST_DATA, headers=headers)
    assert rv.status_code == 422


def test_device_post_method_string_reg_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = 'abc-xyz'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'Registration Request not found.'


def test_device_post_method_empty_reg_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = ''

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'Registration Request not found.'


def test_device_post_method_missing_reg_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data.pop('reg_id')

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'Registration Request not found.'


def test_device_post_method_missing_user_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data.pop('user_id')

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'user_id' in data
    assert data['user_id'][0] == 'user_id is required'


def test_device_post_method_empty_user_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['user_id'] = ''

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'user_id' in data
    assert data['user_id'][0] == 'Permission denied for this request'


def test_device_post_method_empty_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = ''

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand value should be between 1 and 1000'


def test_device_post_method_missing_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data.pop('brand')

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'Brand is required'


def test_device_post_method_start_with_tab_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = '\tapple'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot start or ends with tabs'


def test_device_post_method_end_with_tab_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = 'apple\t'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot start or ends with tabs'


def test_device_post_method_start_with_space_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = ' apple'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot start or ends with spaces'


def test_device_post_method_end_with_space_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = 'apple  '

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot start or ends with spaces'


def test_device_post_method_start_with_line_break_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = '\napple'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot end with line breaks'


def test_device_post_method_end_with_line_break_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = 'apple\n'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot end with line breaks'


def test_device_post_method_empty_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = ''

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system value should be between 1 and 1000'


def test_device_post_method_missing_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data.pop('operating_system')

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'Operating system is required'


def test_device_post_method_start_with_tab_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = '\tosx'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot start or ends with tabs'


def test_device_post_method_end_with_tab_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = 'osx\t'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot start or ends with tabs'


def test_device_post_method_start_with_space_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = ' osx'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot start or ends with spaces'


def test_device_post_method_end_with_space_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = 'osx  '

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot start or ends with spaces'


def test_device_post_method_start_with_line_break_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = '\nosx'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot end with line breaks'


def test_device_post_method_end_with_line_break_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = 'osx\n'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot end with line breaks'


def test_device_post_method_empty_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = ''

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name value should be between 1 and 1000'


def test_device_post_method_missing_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data.pop('model_name')

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'Model name is required'


def test_device_post_method_start_with_tab_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = '\tosx'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot start or ends with tabs'


def test_device_post_method_end_with_tab_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = 'osx\t'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot start or ends with tabs'


def test_device_post_method_start_with_space_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = ' osx'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot start or ends with spaces'


def test_device_post_method_end_with_space_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = 'osx  '

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot start or ends with spaces'


def test_device_post_method_start_with_line_break_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = '\nosx'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot end with line breaks'


def test_device_post_method_end_with_line_break_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = 'osx\n'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot end with line breaks'


def test_device_post_method_empty_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = ''

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number value should be between 1 and 1000'


def test_device_post_method_missing_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data.pop('model_num')

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'Model number is required'


def test_device_post_method_start_with_tab_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = '\tiphone-x'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot start or ends with tabs'


def test_device_post_method_end_with_tab_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = 'iphone-x\t'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot start or ends with tabs'


def test_device_post_method_start_with_space_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = ' iphone-x'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot start or ends with spaces'


def test_device_post_method_end_with_space_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = 'iphone-x  '

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot start or ends with spaces'


def test_device_post_method_start_with_line_break_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = '\niphone-x'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot end with line breaks'


def test_device_post_method_end_with_line_break_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = 'iphone-x\n'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot end with line breaks'


def test_device_post_method_empty_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = ''

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_post_method_missing_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data.pop('device_type')

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'device_type' in data
    assert data['device_type'][0] == 'Device type is required'


def test_device_post_method_start_with_tab_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = '\tSmartphone'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_post_method_end_with_tab_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = 'Smartphone\t'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_post_method_start_with_space_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = ' Smartphone'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_post_method_end_with_space_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = 'Smartphone  '

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_post_method_start_with_line_break_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = '\nSmartphone'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_post_method_end_with_line_break_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = 'Smartphone\n'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_post_method_missing_technologies(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data.pop('technologies')

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_device_post_method_end_with_empty_technologies(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['technologies'] = ''

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_device_post_method_end_with_invalid_technologies(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['technologies'] = 'test'

    rv = flask_app.post(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_device_put_method_reg_id_not_found(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=REQUEST_DATA, headers=headers)
    assert rv.status_code == 422


def test_device_put_method_string_reg_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = 'abc-xyz'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'Registration Request not found.'


def test_device_put_method_empty_reg_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = ''

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'Registration Request not found.'


def test_device_put_method_missing_reg_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data.pop('reg_id')

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'message' in data
    assert data['message'][0] == 'Registration Request not found.'


def test_device_put_method_update_not_allowed(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    request_data['reg_id'] = registration.id

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))

    assert rv.status_code == 422
    assert 'status' in data
    assert data['status'][0] == 'The request status is New Request, which cannot be updated'


def test_device_put_method_missing_user_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data.pop('user_id')

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'user_id' in data
    assert data['user_id'][0] == 'user_id is required'


def test_device_put_method_empty_user_id(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['user_id'] = ''

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'user_id' in data
    assert data['user_id'][0] == 'Permission denied for this request'


def test_device_put_method_start_with_tab_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = '\tapple'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot start or ends with tabs'


def test_device_put_method_end_with_tab_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = 'apple\t'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot start or ends with tabs'


def test_device_put_method_start_with_space_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = ' apple'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot start or ends with spaces'


def test_device_put_method_end_with_space_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = 'apple  '

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot start or ends with spaces'


def test_device_put_method_start_with_line_break_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = '\napple'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot end with line breaks'


def test_device_put_method_end_with_line_break_brand(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['brand'] = 'apple\n'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'brand' in data
    assert data['brand'][0] == 'brand cannot end with line breaks'


def test_device_put_method_empty_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = ''

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system value should be between 1 and 1000'


def test_device_put_method_start_with_tab_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = '\tosx'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot start or ends with tabs'


def test_device_put_method_end_with_tab_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = 'osx\t'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot start or ends with tabs'


def test_device_put_method_start_with_space_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = ' osx'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot start or ends with spaces'


def test_device_put_method_end_with_space_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = 'osx  '

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot start or ends with spaces'


def test_device_put_method_start_with_line_break_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = '\nosx'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot end with line breaks'


def test_device_put_method_end_with_line_break_operating_system(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['operating_system'] = 'osx\n'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'operating_system' in data
    assert data['operating_system'][0] == 'operating system cannot end with line breaks'


def test_device_put_method_empty_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = ''

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name value should be between 1 and 1000'


def test_device_put_method_start_with_tab_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = '\tosx'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot start or ends with tabs'


def test_device_put_method_end_with_tab_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = 'osx\t'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot start or ends with tabs'


def test_device_put_method_start_with_space_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = ' osx'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot start or ends with spaces'


def test_device_put_method_end_with_space_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = 'osx  '

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot start or ends with spaces'


def test_device_put_method_start_with_line_break_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = '\nosx'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot end with line breaks'


def test_device_put_method_end_with_line_break_model_name(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_name'] = 'osx\n'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_name' in data
    assert data['model_name'][0] == 'model name cannot end with line breaks'


def test_device_put_method_empty_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = ''

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number value should be between 1 and 1000'


def test_device_put_method_start_with_tab_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = '\tiphone-x'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot start or ends with tabs'


def test_device_put_method_end_with_tab_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = 'iphone-x\t'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot start or ends with tabs'


def test_device_put_method_start_with_space_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = ' iphone-x'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot start or ends with spaces'


def test_device_put_method_end_with_space_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = 'iphone-x  '

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot start or ends with spaces'


def test_device_put_method_start_with_line_break_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = '\niphone-x'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot end with line breaks'


def test_device_put_method_end_with_line_break_model_num(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['model_num'] = 'iphone-x\n'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    data = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 422
    assert 'model_num' in data
    assert data['model_num'][0] == 'model number cannot end with line breaks'


def test_device_put_method_empty_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = ''

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_put_method_start_with_tab_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = '\tSmartphone'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_put_method_end_with_tab_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = 'Smartphone\t'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_put_method_start_with_space_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = ' Smartphone'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_put_method_end_with_space_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = 'Smartphone  '

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_put_method_start_with_line_break_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = '\nSmartphone'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_put_method_end_with_line_break_device_type(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['device_type'] = 'Smartphone\n'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 500


def test_device_put_method_end_with_empty_technologies(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['technologies'] = ''

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 422


def test_device_put_method_end_with_invalid_technologies(flask_app, db):  # pylint: disable=unused-argument
    """ To verify that registration device
        method is working properly and response is correct"""

    registration = create_registration(REG_REQ_DATA, uuid.uuid4())
    registration.update_status('Pending Review')
    headers = {'Content-Type': 'multipart/form-data'}

    request_data = copy.deepcopy(REQUEST_DATA)
    request_data['reg_id'] = registration.id
    request_data['technologies'] = 'test'

    rv = flask_app.put(DEVICE_REGISTRATION_API, data=request_data, headers=headers)
    assert rv.status_code == 422
