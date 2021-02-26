"""
module for assign-reviewer api test

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
from sqlalchemy import text
from app.api.v1.models.approvedimeis import ApprovedImeis

# api urls
ASSOCIATION_API = 'api/v1/associate'
ASSOCIATION_DUPLICATE_API = 'api/v1/associate_duplicate'


def test_with_invalid_params(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds with proper error messages when invalid params supplied."""
    headers = {'Content-Type': 'application/json'}
    body_data = {
        "imei": "",
        "uid": "4410377898273"
    }
    rv = flask_app.post(ASSOCIATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422


def test_put_method_not_allowed(flask_app):
    """Verify that PUT method is not allowed."""
    rv = flask_app.put(ASSOCIATION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed."""
    rv = flask_app.delete(ASSOCIATION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_bulk_insert_imeis():  # pylint: disable=unused-argument
    """Verify that the bulk_insert_imeis() works as expected."""
    imei_list = ['67895678901234', '76545678906548', '54375699900000', '35282004000637', '35282004000638',
                 '35282004000639', '35282004000640', '35282004000641', '35282004000642', '35282004000643',
                 '35282004000644', '35282004000645', '35282004000646', '35282004000647', '35282004000648',
                 '35282004000649', '35282004000650', '35282004000651', '35282004000652']
    request_id = 2376322
    status = 'whitelist'
    delta_status = 'delta status'
    imeis = [ApprovedImeis(imei, request_id, status, delta_status) for imei in imei_list]
    ApprovedImeis.bulk_insert_imeis(imeis)


def test_association(flask_app):
    headers = {'Content-Type': 'application/json'}
    body_data = {
        "imei": "76545678906548",
        "uid": "4410377898273"
    }
    rv = flask_app.post(ASSOCIATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == "IMEI has been associated with the given Uid"


def test_with_same_imei_again(flask_app):
    headers = {'Content-Type': 'application/json'}
    body_data = {
        "imei": "76545678906548",
        "uid": "4410377898273"
    }
    rv = flask_app.post(ASSOCIATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 409
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == "IMEI already associated wih the same uid"


def test_with_unregistered_imei(flask_app):
    headers = {'Content-Type': 'application/json'}
    body_data = {
        "imei": "76545678906540",
        "uid": "4410377898273"
    }
    rv = flask_app.post(ASSOCIATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 406
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == 'IMEI not registered please register first'


def test_with_duplicate_imei(flask_app):
    headers = {'Content-Type': 'application/json'}
    body_data = {
        "imei": "76545678906548",
        "uid": "4410377898272"
    }
    rv = flask_app.post(ASSOCIATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == 'IMEI already associated you want to associate duplicate?'


def test_device_limit(flask_app):
    headers = {'Content-Type': 'application/json'}
    imei_list = ['67895678901234', '76545678906548', '54375699900000', '35282004000637', '35282004000638',
                 '35282004000639', '35282004000640', '35282004000641', '35282004000642', '35282004000643',
                 '35282004000644', '35282004000645']
    for imei in imei_list:
        body_data = {
            "imei": imei,
            "uid": "4410377898273"
        }
        flask_app.post(ASSOCIATION_API, data=json.dumps(body_data), headers=headers)

    # associating 11th device
    body_data = {
        "imei": '35282004000645',
        "uid": "4410377898273"
    }
    rv = flask_app.post(ASSOCIATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 406
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == 'Maximum number of devices have already been associated with this UID'


def test_grace_period(flask_app):
    headers = {'Content-Type': 'application/json'}
    body_data = {
        "imei": "76545678906548",
        "uid": "4410377898272"
    }
    rv = flask_app.post(ASSOCIATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == 'IMEI already associated you want to associate duplicate?'

    body_data = {
        "imei": "76545678906548",
        "uid": "4410377898272",
        "choice": True
    }
    rv = flask_app.post(ASSOCIATION_DUPLICATE_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == 'IMEI has been associated as duplicate.'


def test_grace_period_when_false(flask_app, app):

    app.config['GRACE_PERIOD'] = False
    headers = {'Content-Type': 'application/json'}
    body_data = {
        "imei": "76545678906548",
        "uid": "4410377898275"
    }
    rv = flask_app.post(ASSOCIATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 409
    data = json.loads(rv.data.decode('utf-8'))
    assert data['message'] == 'imei already associated'


def test_associated_imei_list(flask_app):
    rv = flask_app.get(ASSOCIATION_API+'/4410377898273')
    assert rv.status_code == 200
    data = json.loads((rv.data.decode('utf-8')))
    assert len(data) == 10

    rv = flask_app.get(ASSOCIATION_API + '/4410377898272')
    assert rv.status_code == 200
    data = json.loads((rv.data.decode('utf-8')))
    assert len(data) == 1

