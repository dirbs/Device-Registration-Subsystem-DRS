"""
Project Initialization package.
Copyright (c) 2018 Qualcomm Technologies, Inc.
 All rights reserved.
 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
 disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
 disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
 products derived from this software without specific prior written permission.
 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""
import sys

from flask_restful import Api
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from app.config import ConfigParser

app = Flask(__name__)
CORS(app)
api = Api(app)

try:
    # read and load DRS base configuration to the app
    config = ConfigParser('etc/config.yml').parse_config()
    CORE_BASE_URL = config['dirbs_core']['base_url']  # core api base url
    GLOBAL_CONF = config['global']  # load & export global configs
    app.config['DRS_UPLOADS'] = config['global']['upload_directory']  # file upload dir
    app.config['DRS_LISTS'] = config['lists']['path']  # lists dir
    app.config['CORE_BASE_URL'] = config['global']['core_api_v2']
    app.config['DVS_BASE_URL'] = config['global']['dvs_api_v1']
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://%s:%s@%s:%s/%s' % \
                                            (config['database']['user'],
                                             config['database']['password'],
                                             config['database']['host'],
                                             config['database']['port'],
                                             config['database']['database'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_POOL_SIZE'] = config['database']['pool_size']
    app.config['SQLALCHEMY_POOL_RECYCLE'] = config['database']['pool_recycle']
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = config['database']['max_overflow']
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = config['database']['pool_timeout']
    # app.config['MAX_CONTENT_LENGTH'] = 28 * 3 * 1024 * 1024

    db = SQLAlchemy(session_options={'autocommit': False})
    db.init_app(app)

    # we really need wild-card import here for now
    from app.api.v1.routes import *  # pylint: disable=wildcard-import

    register_docs()

# FIXME: fix broader exception, enable warning
except Exception as e:  # pylint: disable=broad-except
    # logger do have these members, disabling warnings
    # pylint: disable=no-member
    app.logger.critical('exception encountered while parsing the config file, see details below')
    app.logger.exception(e)
    sys.exit(1)
