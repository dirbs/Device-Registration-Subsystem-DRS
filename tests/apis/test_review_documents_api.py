"""
module for review documents api tests

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

from tests._helpers import create_dummy_request, create_dummy_devices, create_dummy_documents

# api urls
DOCUMENTS_API = 'api/v1/review/documents'


def test_with_invalid_params(flask_app):
    """Verify that the documents api responds correctly when given invalid input parameters."""
    # str instead of int in request_id field
    request_id = 'abcd'
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(DOCUMENTS_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('request_id') == ["Bad 'request_id':'abcd' argument format. Accepts only integer"]

    # int instead of str in request_type field
    request_id = 12332
    request_type = 2
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(DOCUMENTS_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('request_type') == ["Bad 'request_type':'2' argument format. Accepts only one of ["
                                        "'registration_request', 'de_registration_request']"]

    # any other str other then registration_request/de_registration_request in request_type field.
    request_type = 'abcd'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(DOCUMENTS_API, request_id, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('request_type') == ["Bad 'request_type':'abcd' argument format. Accepts only one of ["
                                        "'registration_request', 'de_registration_request']"]

    # missing request_id param
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_type={1}'.format(DOCUMENTS_API, request_type))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_id is required']

    # missing request_type param
    request_id = 1
    rv = flask_app.get('{0}?request_id={1}'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['error'] == ['request_type is required']


def test_request_not_exists(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds with correct message when request_id is
    invalid i.e request does not exists in the system.
    """
    # registration request test
    request_id = 123713667821923923626328
    request_type = 'registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(DOCUMENTS_API, request_id, request_type))
    assert rv.status_code == 204

    # de-registration request test
    request_id = 123713667821923923626328
    request_type = 'de_registration_request'
    rv = flask_app.get('{0}?request_id={1}&request_type={2}'.format(DOCUMENTS_API, request_id, request_type))
    assert rv.status_code == 204


def test_document_api(flask_app, app, db):
    """Verify that the api responds with correct path and file name of a document."""
    # registration request
    data = {
        'registration': {
            'device_count': 2,
            'imei_per_device': 1,
            'imeis': "[['86834403015010', '868344039012345']]",
            'm_location': 'local',
            'user_name': 'imei stat user 1',
            'user_id': 'imei-stat-user-1'
        },
        'devices': {
            'brand': 'samsung',
            'operating_system': 'android',
            'model_name': 's9',
            'model_num': '30jjd',
            'device_type': 'Smartphone',
            'technologies': '2G,3G,4G'
        },
        'documents': [
            {'label': 'shipment document', 'file_name': 'shipment.pdf'},
            {'label': 'authorization document', 'file_name': 'authorize.pdf'},
            {'label': 'certificate document', 'file_name': 'certf.pdf'},
        ]
    }

    request = create_dummy_request(data.get('registration'), 'Registration')
    request = create_dummy_devices(data.get('devices'), 'Registration', request)
    request = create_dummy_documents(data.get('documents'), 'Registration', request, app)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=registration_request'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))['documents']
    for document in data:
        assert document.get('document_type') in ['shipment document', 'authorization document', 'certificate document']
        assert document.get('link')

    # de registration
    de_registration_data = {
        'file': 'de-reg-test-file.txt',
        'device_count': 1,
        'user_id': 'imei-stat-user-2',
        'user_name': 'assign rev user 1',
        'reason': 'because we have to run tests successfully'
    }
    request = create_dummy_request(de_registration_data, 'De_Registration')
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
    documents = [
            {'label': 'shipment document', 'file_name': 'shipment.pdf'},
            {'label': 'authorization document', 'file_name': 'authorize.pdf'},
            {'label': 'certificate document', 'file_name': 'certf.pdf'},
        ]
    request = create_dummy_devices(device_data, 'De_Registration', request, db, file_content=['357321082345123'],
                                   file_path='{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id,
                                                                  de_registration_data.get('file')))
    request = create_dummy_documents(documents, 'De-Registration', request, app)
    assert request
    request_id = request.id
    rv = flask_app.get('{0}?request_id={1}&request_type=de_registration_request'.format(DOCUMENTS_API, request_id))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))['documents']
    for document in data:
        assert document.get('document_type') in ['shipment document', 'authorization document', 'certificate document']
        assert document.get('link')


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed on request-documents api."""
    rv = flask_app.post(DOCUMENTS_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed on request-documents api."""
    rv = flask_app.delete(DOCUMENTS_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_put_method_not_allowed(flask_app):
    """Verify that PUT method is not allowed on request-documents api."""
    rv = flask_app.put(DOCUMENTS_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
