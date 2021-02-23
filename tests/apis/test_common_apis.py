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
import os
import json

from app.api.v1.models.status import Status
from app.api.v1.models.devicetype import DeviceType
from app.api.v1.models.documents import Documents
from app.api.v1.models.technologies import Technologies
from app.api.v1.schema.common import ServerConfigs as ServerConfigsSchema

# apis urls
# all apis urls should be defined on a single point
SERVER_CONFIGS = 'api/v1/config/server-config'
FILE_DOWNLOADS = 'api/v1/files/download'


# db fixture needed here for db operations so disable pylint warning
# flask_app fixture should be here so disable pylint warning
def test_server_config_api(flask_app, db):  # pylint: disable=unused-argument
    """To verify that the server config apis response is correct as
    per data in database.
    """
    # get data from database
    status_types = Status.get_status_types()
    device_types = DeviceType.get_device_types()
    technologies = Technologies.get_technologies()
    documents = {
        'registration': Documents.get_documents('registration'),
        'de_registration': Documents.get_documents('deregistration')
    }
    expected_response = ServerConfigsSchema().dump(dict(technologies=technologies,
                                                        documents=documents,
                                                        status_types=status_types,
                                                        device_types=device_types)).data

    rv = flask_app.get(SERVER_CONFIGS)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data == expected_response


def test_post_method_not_allowed_on_server_configs(flask_app):
    """Verify that POST method is not allowed on config/server-configs apis."""
    rv = flask_app.post(SERVER_CONFIGS)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_put_method_not_allowed_on_server_configs(flask_app):
    """Verify that PUT method is not allowed on config/server-configs apis."""
    rv = flask_app.put(SERVER_CONFIGS)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed_on_server_configs(flask_app):
    """Verify that DELETE method is not allowed on config/server-configs apis."""
    rv = flask_app.delete(SERVER_CONFIGS)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_file_download_api(flask_app):
    """Verify that the file download api downloads a file provided the correct path
    and vice versa.
    """
    project_path = os.getcwd()

    # test with correct path
    file_path = '{working_dir}/tests/unittest_data/config/config.yml'.format(working_dir=project_path)
    api_url = '{api}?path={file_path}'.format(api=FILE_DOWNLOADS, file_path=file_path)
    rv = flask_app.get(api_url)
    assert rv.status_code == 200

    # test with incorrect path
    file_path = '{working_dir}/tests/unittest_data/config/abcd.yml'.format(working_dir=project_path)
    api_url = '{api}?path={file_path}'.format(api=FILE_DOWNLOADS, file_path=file_path)
    rv = flask_app.get(api_url)
    assert rv.status_code == 400
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('error')[0] == 'file not found or bad file path'

    # test with empty file path
    file_path = ''
    api_url = '{api}?path={file_path}'.format(api=FILE_DOWNLOADS, file_path=file_path)
    rv = flask_app.get(api_url)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('error')[0] == 'path cannot be empty'

    # test with no path var
    rv = flask_app.get(FILE_DOWNLOADS)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('error')[0] == 'path cannot be empty'


def test_post_method_not_allowed_on_file_downloads(flask_app):
    """Verify that POST method is not allowed on file-downloads apis."""
    rv = flask_app.post(FILE_DOWNLOADS)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_put_method_not_allowed_on_file_downloads(flask_app):
    """Verify that PUT method is not allowed on file-downloads apis."""
    rv = flask_app.put(FILE_DOWNLOADS)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed_on_file_downloads(flask_app):
    """Verify that DELETE method is not allowed on file-downloads apis."""
    rv = flask_app.delete(FILE_DOWNLOADS)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
