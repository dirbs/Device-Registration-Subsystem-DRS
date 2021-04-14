"""
module for report apis test

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
import os
import json
import copy

from tests._helpers import create_dummy_devices, create_dummy_documents, \
    create_processed_dummy_request, create_assigned_dummy_request, create_dummy_request
from tests.apis.test_registration_request_apis import REQUEST_DATA as REG_REQ_DATA


# apis urls
# all apis urls should be defined on a single point
DASHBOARD_API = 'api/v1/dashboard/report'
IMEI_REPORT_PERMISSION = 'api/v1/report/permission'
IMEI_REPORT_DOWNLAOD = 'api/v1/report/download'

USER_NAME = 'test-abc'
USER_ID = '17102'
REVIEWER_USER = 'reviewer'
EXPORTER_USER = 'exporter'
IMPORTER_USER = 'importer'

DE_REG_REQUEST_DATA = {
    'device_count': 1,
    'user_name': USER_NAME,
    'user_id': USER_ID,
    'reason': 'exporting devices to another country'
}

REG_REQUEST_DATA = {
            'device_count': 2,
            'imei_per_device': 1,
            'imeis': "[['86834403015010', '868344039012345']]",
            'm_location': 'local',
            'user_name': 'imei stat user 1',
            'user_id': 'imei-stat-user-1'
        }


def test_dashboard_reports_for_reviewer(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    de_reg_request = create_processed_dummy_request(DE_REG_REQUEST_DATA, 'De-Registration')
    reg_request = create_processed_dummy_request(REG_REQUEST_DATA, 'Registration')

    url = "{0}?user_id={1}&user_type={2}".format(DASHBOARD_API, USER_ID, REVIEWER_USER)
    rv = flask_app.get(url)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))

    assert data['user_id'] == USER_ID
    assert data['user_type'] == REVIEWER_USER

    assert data['registration']
    assert data['de-registration']

    assert data['registration']['pending_review_count']
    assert data['registration']['latest_pending_requests']

    assert data['de-registration']['pending_review_count']
    assert data['de-registration']['latest_pending_requests']

    assert data['registration']['latest_pending_requests'][0]['id'] == reg_request.id
    assert data['de-registration']['latest_pending_requests'][0]['id'] == de_reg_request.id


def test_registration_set_imei_report_permissions_not_assigned_request(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    reg_request = create_processed_dummy_request(REG_REQUEST_DATA, 'Registration')
    url = IMEI_REPORT_PERMISSION
    request_data = {
        "request_type": "registration_request",
        "request_id": "{0}".format(reg_request.id),
        "user_type": "reviewer",
        "user_id": "{0}".format(USER_ID)
    }
    headers = {'Content-Type': 'application/json'}
    rv = flask_app.post(url, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 422


def test_registration_set_imei_report_permissions_assigned_request(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    reg_request = create_assigned_dummy_request(REG_REQUEST_DATA, 'Registration', USER_ID, USER_NAME)
    url = IMEI_REPORT_PERMISSION
    request_data = {
        "request_type": "registration_request",
        "request_id": "{0}".format(reg_request.id),
        "user_type": "reviewer",
        "user_id": "{0}".format(USER_ID)
    }
    headers = {'Content-Type': 'application/json'}
    rv = flask_app.post(url, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 200


def test_registration_set_imei_report_permissions_report_not_found(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    reg_request = create_dummy_request(REG_REQUEST_DATA, 'Registration')
    url = IMEI_REPORT_PERMISSION
    request_data = {
        "request_type": "registration_request",
        "request_id": "{0}".format(reg_request.id),
        "user_type": "reviewer",
        "user_id": "{0}".format(USER_ID)
    }
    headers = {'Content-Type': 'application/json'}
    rv = flask_app.post(url, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 422


def test_de_registration_set_imei_report_permissions_not_assigned_request(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    de_reg_request = create_processed_dummy_request(DE_REG_REQUEST_DATA, 'De-Registration')
    url = IMEI_REPORT_PERMISSION
    request_data = {
        "request_type": "de_registration_request",
        "request_id": "{0}".format(de_reg_request.id),
        "user_type": "reviewer",
        "user_id": "{0}".format(USER_ID)
    }
    headers = {'Content-Type': 'application/json'}
    rv = flask_app.post(url, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 422


def test_de_registration_set_imei_report_permissions_assigned_request(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    de_reg_request = create_assigned_dummy_request(DE_REG_REQUEST_DATA, 'De-Registration', USER_ID, USER_NAME)
    url = IMEI_REPORT_PERMISSION
    request_data = {
        "request_type": "de_registration_request",
        "request_id": "{0}".format(de_reg_request.id),
        "user_type": "reviewer",
        "user_id": "{0}".format(USER_ID)
    }
    headers = {'Content-Type': 'application/json'}
    rv = flask_app.post(url, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 200


def test_de_registration_set_imei_report_permissions_report_not_found(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    reg_request = create_dummy_request(DE_REG_REQUEST_DATA, 'De-Registration')
    url = IMEI_REPORT_PERMISSION
    request_data = {
        "request_type": "de_registration_request",
        "request_id": "{0}".format(reg_request.id),
        "user_type": "reviewer",
        "user_id": "{0}".format(USER_ID)
    }
    headers = {'Content-Type': 'application/json'}
    rv = flask_app.post(url, data=json.dumps(request_data), headers=headers)
    assert rv.status_code == 422


def test_imei_report_download_user_not_found(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    reg_request = create_processed_dummy_request(REG_REQUEST_DATA, 'Registration')
    url = "{0}?request_type={1}&request_id={2}&user_type={3}&use_id={4}".\
        format(IMEI_REPORT_DOWNLAOD, 'registration_request', reg_request.id, 'reviewer', None)
    rv = flask_app.get(url)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))

    assert 'error' in data
    assert data['error'][0] == 'user_id is required'


def test_imei_report_download_request_id_not_found(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    reg_request = create_processed_dummy_request(REG_REQUEST_DATA, 'Registration')
    url = "{0}?request_type={1}&request_i={2}&user_type={3}&user_id={4}".\
        format(IMEI_REPORT_DOWNLAOD, 'registration_request', reg_request.id, 'reviewer', None)
    rv = flask_app.get(url)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))

    assert 'error' in data
    assert data['error'][0] == 'request_id is required'


def test_imei_report_download_not_allowed(flask_app, db):  # pylint: disable=unused-argument
    """Verify that POST method to test dashboard reports for reviewer user"""

    reg_request = create_processed_dummy_request(REG_REQUEST_DATA, 'Registration')
    url = "{0}?request_type={1}&request_id={2}&user_type={3}&user_id={4}".\
        format(IMEI_REPORT_DOWNLAOD, 'registration_request', reg_request.id, 'importer', 1234)
    rv = flask_app.get(url)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))

    assert 'message' in data
    assert data['message'][0] == 'Report not allowed.'
