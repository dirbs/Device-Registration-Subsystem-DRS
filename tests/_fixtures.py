"""
Reusable py.test fixtures for unit tests.
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
import re
import json
import copy
import shutil
from os import path

import pytest
import httpretty

from testing.postgresql import Postgresql

from app.config import ConfigParser
from tests._helpers import seed_database, create_views


@pytest.fixture(scope='session')
def mocked_config():
    """Fixture for mocking config.yml so that tests do not depend on user config at all."""
    mocked_config_path = path.abspath(path.dirname(__file__) + '/unittest_data/config/config.yml')
    config = ConfigParser(mocked_config_path).parse_config()

    yield config


# pylint: disable=redefined-outer-name
@pytest.yield_fixture(scope='session')
def app(mocked_config, tmpdir_factory):
    """Method to create an app for testing."""
    # need to import this late as it might have side effects
    from app import app as app_

    # need to save old configurations of the app
    # to restore them later upon tear down
    old_url_map = copy.copy(app_.url_map)
    old_view_functions = copy.copy(app_.view_functions)
    app_.testing = True
    app_.debug = False
    old_config = copy.copy(app_.config)

    # initialize temp database and yield app
    postgresql = Postgresql()

    # monkey patch temp dirs
    temp_lists = tmpdir_factory.mktemp('lists')
    mocked_config['lists']['path'] = str(temp_lists)
    temp_uploads = tmpdir_factory.mktemp('uploads')
    mocked_config['global']['upload_directory'] = str(temp_uploads)
    app_.config['drs_config'] = mocked_config
    app_.config['SQLALCHEMY_DATABASE_URI'] = postgresql.url()
    app_.config['DRS_UPLOADS'] = str(temp_uploads)
    app_.config['DRS_LISTS'] = str(temp_lists)
    app_.config['CORE_BASE_URL'] = mocked_config['global']['core_api_v2']
    app_.config['DVS_BASE_URL'] = mocked_config['global']['dvs_api_v1']

    yield app_

    # restore old configs after successful session
    app_.url_map = old_url_map
    app_.view_functions = old_view_functions
    app_.config = old_config
    shutil.rmtree(str(temp_lists))
    shutil.rmtree(str(temp_uploads))
    postgresql.stop()


@pytest.fixture(scope='session')
def flask_app(app):
    """fixture for injecting flask test client into every test."""
    yield app.test_client()


@pytest.yield_fixture(scope='session')
def db(app):
    """fixture to inject temp db instance into tests."""
    # need to import this late it might cause problems
    from app import db

    # create and configure database
    db.app = app
    db.create_all()
    seed_database(db)
    create_views(db)
    yield db

    # teardown database
    db.engine.execute('DROP TABLE technologies CASCADE')
    db.engine.execute('DROP TABLE status CASCADE')
    db.engine.execute('DROP TABLE devicetype CASCADE')
    db.engine.execute('DROP TABLE documents CASCADE')
    db.session.close()
    db.drop_all()


@pytest.yield_fixture(scope='session')
def session(db):
    """Fixture for injecting database connection session into the tests."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)
    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()


@pytest.yield_fixture(scope='session')
def dirbs_core(app):
    """
    Mock server fixture to simulate DIRBS Core API behaviours.
    Monkey patch DIRBS-Core calls made by DRS."""
    httpretty.enable()
    single_tac_response = {
        "gsma": {
            "allocation_date": "string",
            "bands": "string",
            "bluetooth": "string",
            "brand_name": "string",
            "device_type": "string",
            "internal_model_name": "string",
            "manufacturer": "string",
            "marketing_name": "string",
            "model_name": "string",
            "nfc": "string",
            "radio_interface": "string",
            "wlan": "string"
        },
        "tac": "string"
    }

    # mock dirbs core single tac apis
    dirbs_core_api = app.config['CORE_BASE_URL']
    httpretty.register_uri(
        httpretty.GET,
        re.compile(r'{0}/tac/\d'.format(dirbs_core_api)),
        body=json.dumps(single_tac_response),
        content_type='application/json')

    # mock dirbs core batch tac apis
    httpretty.register_uri(
        httpretty.POST,
        '{0}/tac'.format(dirbs_core_api),
        body=json.dumps({"results": [single_tac_response]}),
        content_type='application/json')

    # mock version api
    version_response = {
        'source_code_version': 'string',
        'code_db_schema_version': 0,
        'db_schema_version': 0,
        'report_schema_version': 0
    }
    httpretty.register_uri(
        httpretty.GET,
        '{0}version'.format(dirbs_core_api),
        body=json.dumps(version_response),
        content_type='application/json'
    )
    yield

    # disable afterwards when not in use to avoid issues with the sockets
    # reset states
    httpretty.disable()
    httpretty.reset()


@pytest.yield_fixture(scope='session')
def dirbs_dvs(app):
    """
    Mock server fixture to simulate DIRBS DVS API behaviours.
    Monkey patch DIRBS-DVS calls made by DRS."""
    httpretty.enable()
    bulk_imei_response = {
        "result": {
            "provisional_non_compliant": 0,
            "seen_on_network": 1,
            "count_per_condition":
                {
                    "local_stolen": 0,
                    "duplicate_large": 0,
                    "duplicate": 0,
                    "not_on_registration_list": 1,
                    "gsma_not_found": 0,
                    "malformed": 0
                },
            "complaint": 0,
            "provisional_compliant": 0,
            "non_complaint": 8,
            "compliant_report_name": "compliant_report80f54be6-b147-4b09-aba1-ada628b6abbc.tsv",
            "verified_imei": 8,
            "stolen": 0,
            "provisional_stolen": 0
        },
        "state": "SUCCESS"
    }

    # mock dirbs core single tac apis
    dirbs_dvs_api = app.config['DVS_BASE_URL']
    httpretty.register_uri(
        httpretty.POST,
        re.compile(r'{0}/drs_bulk/\d'.format(dirbs_dvs_api)),
        body=json.dumps(bulk_imei_response),
        content_type='application/json')

    bulk_status_response = {'state': 'COMPLETED'}
    httpretty.register_uri(
        httpretty.GET,
        re.compile(r'{0}/bulkstatus/\d'.format(dirbs_dvs_api)),
        body=json.dumps(bulk_status_response),
        content_type='application/json')
    yield

    # disable afterwards when not in use to avoid issues with the sockets
    # reset states
    httpretty.disable()
    httpretty.reset()
