"""
Utilities unit tests

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

import uuid
import os
from app.api.v1.helpers.utilities import Utilities
from tests._helpers import create_registration
from tests.apis.test_registration_request_apis import REQUEST_DATA as REG_REQ_DATA


IMEIS = ['12345678765432', '12345678986434',
         '23434343450987', '23434343565443']

tacs = ['12345678', '3456786']

IMEI_TAC_MAP = {
    '12345678': ['12345678765432', '12345678986434'],
    '23434343': ['23434343450987', '23434343565443']
}


def test_remove_directory(app, session):  # pylint: disable=unused-argument
    """Verify that the remove function works correctly."""
    tracking_id = uuid.uuid4()
    complete_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id))
    Utilities.create_directory(tracking_id)
    assert os.path.isdir(complete_path)
    Utilities.remove_directory(tracking_id)
    assert os.path.isdir(complete_path) is False


def test_remove_file(app, session):  # pylint: disable=unused-argument
    """Verify that the remove function works correctly."""
    tracking_id = uuid.uuid4()
    complete_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id))
    Utilities.create_directory(tracking_id)
    assert os.path.isdir(complete_path)
    response = Utilities.remove_file('file.txt', tracking_id)
    assert response == 'file is missing'


def test_extract_imeis(app, session):  # pylint: disable=unused-argument
    """Verify that the extract imeis function works correctly."""

    response = Utilities.extract_imeis(IMEI_TAC_MAP)
    assert len(response) == 4
    assert '12345678765432' in response
    assert '12345678986434' in response
    assert '23434343450987' in response
    assert '23434343565443' in response


def test_generate_summary(app, session, dirbs_dvs):  # pylint: disable=unused-argument
    """Verify that the generate function works correctly."""

    tracking_id = uuid.uuid4()
    request = create_registration(REG_REQ_DATA, tracking_id)
    Utilities.create_directory(tracking_id)
    assert request.tracking_id == tracking_id
    response = Utilities.generate_summary(IMEIS, tracking_id)
    # Async process
    assert not response


def test_pool_summary_request(app, session, dirbs_dvs):  # pylint: disable=unused-argument
    """Verify that the poll_summary function works correctly."""

    tracking_id = uuid.uuid4()
    request = create_registration(REG_REQ_DATA, tracking_id)
    Utilities.create_directory(tracking_id)
    assert request.tracking_id == tracking_id
    response = Utilities.pool_summary_request('mock-task-id', request, app)
    assert request.tracking_id == str(tracking_id)
    assert response is None


def test_de_register_bulk_imeis(app, session):  # pylint: disable=unused-argument
    """Verify that the de_register_imeis function works correctly."""

    response = Utilities.de_register_imeis(IMEIS)
    assert response is False


def test_de_register_single_imeis(app, session):  # pylint: disable=unused-argument
    """Verify that the de_register_imeis function works correctly."""

    response = Utilities.de_register_imeis(IMEIS[0])
    assert response is False


def test_bulk_get_devices_description(app, session, dirbs_core):  # pylint: disable=unused-argument
    """Verify that the get_device_description function works correctly."""

    response = Utilities.get_devices_description(tacs)
    assert response
    assert 'gsma' in response['results'][0]
    assert response['results'][0]['gsma']['allocation_date'] == 'string'
    assert response['results'][0]['tac'] == 'string'


def test_single_get_devices_description(app, session, dirbs_core):  # pylint: disable=unused-argument
    """Verify that the get_device_description function works correctly."""

    response = Utilities.get_devices_description([tacs[0]])
    assert response
    assert 'gsma' in response
    assert response['gsma']['allocation_date'] == 'string'
    assert response['tac'] == 'string'


def test_index_exist_idx(app, db):  # pylint: disable=unused-argument
    """Verify that the index exits function works correctly."""

    response = Utilities.exist_idx('test-index')
    assert response is False


def test_split_chunks(app):  # pylint: disable=unused-argument
    """Verify that the split chunks function works correctly."""

    response = Utilities.split_chunks(IMEIS, 2)
    assert response


def test_split_imeis(app):  # pylint: disable=unused-argument
    """Verify that the split imeis function works correctly."""

    imeis = "12345678976543, 34567897654321"
    response = Utilities.split_imeis(imeis)
    assert response
    assert len(response) == 2


def test_convert_to_mbs(app):  # pylint: disable=unused-argument
    """Verify that the convert to mbs function works correctly."""

    filesize = 1024 * 1024

    response = Utilities.convert_to_mb(filesize)
    assert response
    assert response == 1
