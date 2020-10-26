"""
module for review imei-classification api tests

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

# api urls
CLASSIFICATION_API = 'api/v1/review/imei-classification'


def test_with_invalid_params(flask_app):
    """Verify that the api responds correctly when invalid/wrong input params supplied."""
    # str instead of int in request_id field
    request_id = 'abcd'
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(CLASSIFICATION_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_id'] == ["Bad 'request_id':'abcd' argument format. Accepts only integer"]

    # int instead of str in request_type field
    request_id = 13123123123132324231312
    request_type = 3
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(CLASSIFICATION_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_type'] == ["Bad 'request_type':'3' argument format. Accepts only one of ["
                                    "'registration_request', 'de_registration_request']"]

    # str other than registration_request/de-registration_request in request_type field
    request_type = 'abc_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(CLASSIFICATION_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['request_type'] == ["Bad 'request_type':'abc_request' argument format. Accepts only one of ["
                                    "'registration_request', 'de_registration_request']"]

    # no request_id argument
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_type={1}'.format(CLASSIFICATION_API, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_id is required']

    # no request_type argument
    request_id = 1
    rv = flask_app.get('{0}?request_id={1}'.format(CLASSIFICATION_API, request_id))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_type is required']


def test_request_not_exists(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds correctly when a request_id is given which does not exists in system."""
    # registration_request test
    request_id = 748574387344767294723704
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(CLASSIFICATION_API, request_id, request_type))
    assert rv.status_code == 204

    # de-registration request test
    request_id = 748574387344767294723704
    request_type = 'de_registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(CLASSIFICATION_API, request_id, request_type))
    assert rv.status_code == 204


def test_imei_classification(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api returns correct imei classification information."""
    # registration request
    registration_data = {
        'device_count': 2,
        'imei_per_device': 1,
        'imeis': "[['86834403015010', '868344039012345']]",
        'm_location': 'local',
        'user_name': '4yyjhhkhkimei stat user 1',
        'user_id': 'imeihfhdhhd-stat-user-1'
    }

    summary = {
        "provisional_compliant": 0,
        "non_complaint": 10,
        "count_per_condition": {
            "not_on_registration_list": 0,
            "on_local_stolen_list": 0,
            "gsma_not_found": 0,
            "duplicate_compound": 0
        },
        "provisional_stolen": 0,
        "compliant_report_name": "compliant_report669f9938-1ffb-468e-b303-f73385a1b9e0.tsv",
        "provisional_non_compliant": 0,
        "complaint": 0,
        "seen_on_network": 0,
        "stolen": 0,
        "verified_imei": 10
    }
    request = create_assigned_dummy_request(registration_data, 'Registration',
                                            '23233eeedev-descp-1', '3323eeedev descp')
    request.update_summary(summary)
    rv = flask_app.get('{0}?request_id={1}&request_type=registration_request'.format(CLASSIFICATION_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['lost_stolen_status']['provisional_stolen'] == 0
    assert data['lost_stolen_status']['stolen'] == 0
    assert data['seen_on_network'] == 0
    assert data['imei_compliance_status']['compliant_imeis'] == 0
    assert data['imei_compliance_status']['non_compliant_imeis'] == 10
    assert data['imei_compliance_status']['provisional_non_compliant'] == 0
    assert data['imei_compliance_status']['provisional_compliant'] == 0
    assert data['per_condition_classification_state']['not_on_registration_list'] == 0
    assert data['per_condition_classification_state']['on_local_stolen_list'] == 0
    assert data['per_condition_classification_state']['gsma_not_found'] == 0
    assert data['per_condition_classification_state']['duplicate_compound'] == 0

    # de-registration
    data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': 'avbvvssign-rev-user-1',
        'user_name': 'avbvbbvssign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_assigned_dummy_request(data, 'De-Registration', 'dew3223ev-descp-1', 'de322ev descp')
    assert request
    request.update_summary(summary)
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(CLASSIFICATION_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['lost_stolen_status']['provisional_stolen'] == 0
    assert data['lost_stolen_status']['stolen'] == 0
    assert data['seen_on_network'] == 0
    assert data['imei_compliance_status']['compliant_imeis'] == 0
    assert data['imei_compliance_status']['non_compliant_imeis'] == 10
    assert data['imei_compliance_status']['provisional_non_compliant'] == 0
    assert data['imei_compliance_status']['provisional_compliant'] == 0
    assert data['per_condition_classification_state']['not_on_registration_list'] == 0
    assert data['per_condition_classification_state']['on_local_stolen_list'] == 0
    assert data['per_condition_classification_state']['gsma_not_found'] == 0
    assert data['per_condition_classification_state']['duplicate_compound'] == 0


def test_empty_classification_state(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds properly if there is no summary in the summary column."""
    # registration
    registration_data = {
        'device_count': 2,
        'imei_per_device': 1,
        'imeis': "[['86834403015010', '868344039012345']]",
        'm_location': 'local',
        'user_name': '3234323imei stat user 1',
        'user_id': '434334imei-stat-user-1'
    }
    request = create_assigned_dummy_request(registration_data, 'Registration', '434dev-descp-1', 'd4343ev descp')
    rv = flask_app.get('{0}?request_id={1}&request_type=registration_request'.format(CLASSIFICATION_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data == {}

    # de-registration
    # de-registration
    data = {
        'file': 'de-reg-test-file',
        'device_count': 1,
        'user_id': '2323323assign-rev-user-1',
        'user_name': '3233assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_assigned_dummy_request(data, 'De-Registration', '323dev-descp-1', '3233dev descp')
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(CLASSIFICATION_API, request.id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data == {}


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed on imei-classification api."""
    rv = flask_app.post(CLASSIFICATION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed on imei-classification api."""
    rv = flask_app.delete(CLASSIFICATION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_put_method_not_allowed(flask_app):
    """Verify that PUT method is not allowed on imei-classification api."""
    rv = flask_app.put(CLASSIFICATION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
