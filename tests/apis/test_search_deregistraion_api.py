"""
module for search registration module api test

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

from tests._helpers import create_dummy_documents, \
    create_dummy_devices, \
    create_assigned_dummy_request, seed_database, \
    create_views

# api urls
SEARCH_API = 'api/v1/search'
DEVICE_REGISTRATION_REQ_API = 'api/v1/deregistration'
DEVICE_DESCRIPTION_API = 'api/v1/review/device-description'
DOCUMENTS_API = 'api/v1/review/documents'


def test_method_not_allowed(flask_app):
    """Verify that GET, PUT, PATCH DELETE method are not allowed """
    rv = flask_app.get(SEARCH_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'

    rv = flask_app.put(SEARCH_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'

    rv = flask_app.delete(SEARCH_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'

    rv = flask_app.patch(SEARCH_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'

def test_valid_search_specs(flask_app, db):
    seed_database(db)
    create_views(db)

    # Check empty result is return
    headers = {'Content-type': 'application/json'}
    body_data = {
        "start": 1,
        "limit": 10,
        "search_specs":
            {
                "group": "reviewer",
                "request_type": 2,
                "user_id": ""
            },
        "search_args":
            {
                "id": "10201112000"
            }
    }

    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['requests'] == []

    body_data['search_args'] = {}
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['requests'] == []


def test_invalid_search_specs(flask_app):
    """Validate request if invalid parameters or values are provided and respond with proper status code."""
    headers = {'Content-type': 'application/json'}
    body_data = {
        "start": 1,
        "limit": 10,
        "search_specs":
            {
                "group": "exporter",
                "request_type": "one",
                "user_id": ""
            },
        "search_args":
            {
            }
    }

    # +ve response with empty result
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == "Request type not found!"

    # no data found
    body_data['search_specs']['group'] = ""
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 404
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == "No data found"

    # empty input parameters
    body_data['search_specs']['group'] = ""
    body_data['search_specs']['request_type'] = ""
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 404
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == "No data found"

    # empty search specs parameters
    body_data['search_specs'] = {}
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 404
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == "Search Specs attributes missing!"


def test_search_invalid_parameters(flask_app):
    """Validate invalid seach specification input parameters and respond with proper status code."""

    headers = {'Content-type': 'application/json'}

    # Reviewer invalid request parameters
    body_data = {
        "start": 1,
        "limit": 10,
        "search_specs":
            {
                "group": "reviewer",
                "request_type": 2,
                "user_id": ""
            },
        "search_args":
            {
                "tracking_id": "string",
                "created_at": "string",
                "updated_at": "string",
                "device_count": "string",
                "status": "string",
                "brand": "string",
                "model_name": "string",
                "operating_system": "string",
                "device_type": "string",
                "imeis": ["string", "string"]
            }
    }
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 404
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == "Not Found"

    body_data["search_specs"]['group'] = 'tester'
    body_data["search_args"] = {}
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 404
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == "No data found"


def test_search_valid_parameters(flask_app, db, app):
    """Validate/Verifies valid search parameters all valid search inputs and respond with proper status code."""
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
                       "model_name": "Nokia 6",
                       "brand_name": "Nokia",
                       "model_num": "TA-1034",
                       "technology": "NONE",
                       "device_type": "Mobile Phone/Feature phone",
                       "count": 2,
                       "operating_system": "Android"
                   }
               ]""",
        'dereg_id': request.id
    }
    documents = [
        {'label': 'shipment document', 'file_name': 'shipment.pdf'},
        {'label': 'authorization document', 'file_name': 'authorize.pdf'},
        {'label': 'certificate document', 'file_name': 'certf.pdf'},
    ]
    request = create_dummy_devices(device_data, 'De_Registration', request, db,
                                   file_content=['357321082345123', '357321082345124'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    request = create_dummy_documents(documents, 'De-Registration', request, app)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 200

    headers = {'Content-type': 'application/json'}

    # Reviewer Valid request parameters
    body_data = {
        "start": 1,
        "limit": 10,
        "search_specs":
            {
                "group": "reviewer",
                "request_type": 2,
                "user_id": ""
            },
        "search_args":
            {
                "id": request.id,
                "tracking_id": request.tracking_id,
                "brand": 'Nokia',
                "created_at": request.created_at.strftime("%Y-%m-%d") + ',' + request.updated_at.strftime("%Y-%m-%d"),
                "updated_at": request.created_at.strftime("%Y-%m-%d") + ',' + request.updated_at.strftime("%Y-%m-%d"),
                "device_count": de_registration_data['device_count'],
                "model_name": device_data['devices'][0]['model_name'],
                "operating_system": device_data['devices'][0]['operating_system'],
                "device_type": device_data['devices'][0]['device_type'],
                "technologies": device_data['devices'][0]['technology'],
            }
    }

    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    body_data['search_args'] = {}
    body_data['search_specs']['group'] = 'exporter'
    body_data['search_specs']['user_id'] = de_registration_data['user_id']
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    body_data['search_args'] = {}
    body_data['search_args']['status'] = "In Review"
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []


def test_technologies(flask_app, db, app):
    """Validate technologies input search parameter and respond with positive result and status code."""

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
                       "model_name": "Nokia 6",
                       "brand_name": "Nokia",
                       "model_num": "TA-1034",
                       "technology": "3G,4G",
                       "device_type": "Mobile Phone/Feature phone",
                       "count": 2,
                       "operating_system": "Android"
                   }
               ]""",
        'dereg_id': request.id
    }
    documents = [
        {'label': 'shipment document', 'file_name': 'shipment.pdf'},
        {'label': 'authorization document', 'file_name': 'authorize.pdf'},
        {'label': 'certificate document', 'file_name': 'certf.pdf'},
    ]
    request = create_dummy_devices(device_data, 'De_Registration', request, db,
                                   file_content=['357321082345123', '357321082345124'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    request = create_dummy_documents(documents, 'De-Registration', request, app)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 200

    headers = {'Content-type': 'application/json'}
    body_data = {
        "start": 1,
        "limit": 10,
        "search_specs":
            {
                "group": "reviewer",
                "request_type": 2,
                "user_id": ""
            },
        "search_args":
            {
                'technologies': ["3G"]
            }
    }

    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    body_data['search_args']['technologies'] = ['3G', '4G']
    body_data["search_args"]['brand'] = device_data['devices'][0]['brand_name']
    body_data["search_args"]['model_name'] = device_data['devices'][0]['model_name']
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    body_data['search_args']['technologies'] = ['3G']
    body_data["search_args"]['brand'] = device_data['devices'][0]['brand_name']
    body_data["search_args"]['model_name'] = device_data['devices'][0]['model_name']
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []


def test_id(flask_app, db, app):
    """Verifies valid id input search parameter and respond with positive result and status code."""

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
                       "model_name": "Nokia 6",
                       "brand_name": "Nokia",
                       "model_num": "TA-1034",
                       "technology": "3G,4G",
                       "device_type": "Mobile Phone/Feature phone",
                       "count": 2,
                       "operating_system": "Android"
                   }
               ]""",
        'dereg_id': request.id
    }
    documents = [
        {'label': 'shipment document', 'file_name': 'shipment.pdf'},
        {'label': 'authorization document', 'file_name': 'authorize.pdf'},
        {'label': 'certificate document', 'file_name': 'certf.pdf'},
    ]
    request = create_dummy_devices(device_data, 'De_Registration', request, db,
                                   file_content=['357321082345123', '357321082345124'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    request = create_dummy_documents(documents, 'De-Registration', request, app)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 200

    headers = {'Content-type': 'application/json'}

    body_data = {
        "start": 1, "limit": 10,
        "search_specs":
            {
                "group": "exporter",
                "request_type": 2,
                "user_id": "assign-rev-user-1"
            },
        "search_args":
            {
            }
    }

    body_data['search_args']['id'] = request.id
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []


def test_device_count(flask_app, db, app):
    """Verifies valid device_count input search parameter
    and respond with positive or empty result and status code."""

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
                       "model_name": "Nokia 6",
                       "brand_name": "Nokia",
                       "model_num": "TA-1034",
                       "technology": "3G,4G",
                       "device_type": "Mobile Phone/Feature phone",
                       "count": 2,
                       "operating_system": "Android"
                   }
               ]""",
        'dereg_id': request.id
    }
    documents = [
        {'label': 'shipment document', 'file_name': 'shipment.pdf'},
        {'label': 'authorization document', 'file_name': 'authorize.pdf'},
        {'label': 'certificate document', 'file_name': 'certf.pdf'},
    ]
    request = create_dummy_devices(device_data, 'De_Registration', request, db,
                                   file_content=['357321082345123', '357321082345124'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    request = create_dummy_documents(documents, 'De-Registration', request, app)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 200

    headers = {'Content-type': 'application/json'}

    body_data = {
        "start": 1, "limit": 10,
        "search_specs":
            {
                "group": "exporter",
                "request_type": 2,
                "user_id": "assign-rev-user-1"
            },
        "search_args":
            {
            }
    }

    body_data['search_args']['device_count'] = request.device_count
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    body_data['search_args']['device_count'] = 10000
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] == []


def test_request_status(flask_app, db, app):
    """Verify/Validate and return all approved and pending request."""

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
                       "model_name": "Nokia 6",
                       "brand_name": "Nokia",
                       "model_num": "TA-1034",
                       "technology": "3G,4G",
                       "device_type": "Mobile Phone/Feature phone",
                       "count": 2,
                       "operating_system": "Android"
                   }
               ]""",
        'dereg_id': request.id
    }
    documents = [
        {'label': 'shipment document', 'file_name': 'shipment.pdf'},
        {'label': 'authorization document', 'file_name': 'authorize.pdf'},
        {'label': 'certificate document', 'file_name': 'certf.pdf'},
    ]
    request = create_dummy_devices(device_data, 'De_Registration', request, db,
                                   file_content=['357321082345123', '357321082345124'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    request = create_dummy_documents(documents, 'De-Registration', request, app)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 200

    headers = {'Content-type': 'application/json'}

    body_data = {
        "start": 1, "limit": 10,
        "search_specs":
            {
                "group": "exporter",
                "request_type": 2,
                "user_id": "assign-rev-user-1"
            },
        "search_args":
            {
            }
    }

    body_data['search_args']['status'] = 'In Review'
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    result = json.loads(rv.data.decode('utf-8'))
    assert rv.status_code == 200
    assert result['requests'] != []

    # Invalid Result
    body_data['search_args'] = {}
    body_data['search_args']['status'] = 'Pending Review'
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] == []


def test_valid_invalid_date(flask_app, db, app):
    """Search by date and return all result of current user and empty search result"""

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
                       "model_name": "Nokia 6",
                       "brand_name": "Nokia",
                       "model_num": "TA-1034",
                       "technology": "3G,4G",
                       "device_type": "Mobile Phone/Feature phone",
                       "count": 2,
                       "operating_system": "Android"
                   }
               ]""",
        'dereg_id': request.id
    }
    documents = [
        {'label': 'shipment document', 'file_name': 'shipment.pdf'},
        {'label': 'authorization document', 'file_name': 'authorize.pdf'},
        {'label': 'certificate document', 'file_name': 'certf.pdf'},
    ]
    request = create_dummy_devices(device_data, 'De_Registration', request, db,
                                   file_content=['357321082345123', '357321082345124'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    request = create_dummy_documents(documents, 'De-Registration', request, app)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 200

    headers = {'Content-type': 'application/json'}

    body_data = {
        "start": 1, "limit": 10,
        "search_specs":
            {
                "group": "exporter",
                "request_type": 2,
                "user_id": "assign-rev-user-1"
            },
        "search_args":
            {
            }
    }

    # Valid Date Check
    body_data['search_args']['created_at'] = \
        request.created_at.strftime("%Y-%m-%d") + ',' + request.created_at.strftime("%Y-%m-%d")
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    body_data['search_args'] = {}
    body_data['search_args']['created_at'] = request.created_at.strftime(
        "%Y-%m-%d") + ',' + request.created_at.strftime("%Y-%m-%d")
    body_data['search_args']['updated_at'] = request.updated_at.strftime(
        "%Y-%m-%d") + ',' + request.updated_at.strftime("%Y-%m-%d")
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    # InValid Date Check
    body_data['search_args'] = {}
    body_data['search_args']['created_at'] = '2020-12-11' + ',' + '2018-12-11'
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] == []


def test_valid_invalid_imeis(flask_app, db, app):
    """Search by IMEI and return all result of current/reviewer user"""

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
                       "model_name": "Nokia 6",
                       "brand_name": "Nokia",
                       "model_num": "TA-1034",
                       "technology": "3G,4G",
                       "device_type": "Mobile Phone/Feature phone",
                       "count": 2,
                       "operating_system": "Android"
                   }
               ]""",
        'dereg_id': request.id
    }
    documents = [
        {'label': 'shipment document', 'file_name': 'shipment.pdf'},
        {'label': 'authorization document', 'file_name': 'authorize.pdf'},
        {'label': 'certificate document', 'file_name': 'certf.pdf'},
    ]
    request = create_dummy_devices(device_data, 'De_Registration', request, db,
                                   file_content=['357321082345123', '357321082345224'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    request = create_dummy_documents(documents, 'De-Registration', request, app)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 200

    sql = "Update deregimei set device_id=1, imei=357321082345123, norm_imei=3573210823451 where id =1"
    db.session.execute(sql)
    sql = "Insert into deregimei(imei, norm_imei, device_id) VALUES('357321082345224', '3573210823452', 1)"
    db.session.execute(sql)

    headers = {'Content-type': 'application/json'}

    body_data = {
        "start": 1, "limit": 10,
        "search_specs":
            {
                "group": "reviewer",
                "request_type": 2,
                "user_id": ""
            },
        "search_args":
            {
                "imeis": ['357321082345123', '357321082345224']
            }
    }

    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    sql = "Update deregimei set device_id=1, imei=357321082345123, norm_imei=3573210823451 where id =1"
    db.session.execute(sql)
    sql = "Insert into deregimei(imei, norm_imei, device_id) VALUES('357321082345224', '3573210823452', 1)"
    db.session.execute(sql)

    body_data["search_args"]['imeis'] = ['357321082345123']
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    sql = "Update deregimei set device_id=1, imei=357321082345123, norm_imei=3573210823451 where id =1"
    db.session.execute(sql)
    sql = "Insert into deregimei(imei, norm_imei, device_id) VALUES('357321082345224', '3573210823452', 1)"
    db.session.execute(sql)

    body_data["search_specs"]['group'] = "exporter"
    body_data["search_specs"]['user_id'] = de_registration_data['user_id']
    body_data["search_args"]['imeis'] = ['357321082345123']
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    sql = "Update deregimei set device_id=1, imei=357321082345123, norm_imei=3573210823451 where id =1"
    db.session.execute(sql)
    sql = "Insert into deregimei(imei, norm_imei, device_id) VALUES('357321082345224', '3573210823452', 1)"
    db.session.execute(sql)

    body_data["search_specs"]['group'] = "exporter"
    body_data["search_specs"]['user_id'] = de_registration_data['user_id']
    body_data["search_args"]['imeis'] = ['357321082345123']
    body_data["search_args"]['brand'] = device_data['devices'][0]['brand_name']
    body_data["search_args"]['model_name'] = device_data['devices'][0]['model_name']
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []

    sql = "Update deregimei set device_id=1, imei=357321082345123, norm_imei=3573210823451 where id =1"
    db.session.execute(sql)
    sql = "Insert into deregimei(imei, norm_imei, device_id) VALUES('357321082345224', '3573210823452', 1)"
    db.session.execute(sql)

    body_data["search_specs"]['group'] = "exporter"
    body_data["search_specs"]['user_id'] = de_registration_data['user_id']
    body_data["search_args"]['imeis'] = ['357321082345123', '357321082345224']
    body_data["search_args"]['brand'] = device_data['devices'][0]['brand_name']
    body_data["search_args"]['model_name'] = device_data['devices'][0]['model_name']
    rv = flask_app.post(SEARCH_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    result = json.loads(rv.data.decode('utf-8'))
    assert result['requests'] != []
