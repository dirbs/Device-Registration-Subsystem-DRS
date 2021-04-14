"""
Project Initialization package.
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
import sys
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from celery import Celery

from datetime import datetime
from flask_restful import Api
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_babel import Babel

from app.config import ConfigParser, ParseException, ConfigApp
from app.serializer import JSONEncoder

# import _strptime to avoid weird issues as described at
# http://bugs.python.org/msg221094
datetime.strptime('', '')

app = Flask(__name__)
app.logger.setLevel('DEBUG')
app.json_encoder = JSONEncoder()
CORS(app)
Api(app)
babel = Babel(app)

# read and load DRS base configuration to the app
try:
    config = ConfigParser('etc/config.yml').parse_config()
except ParseException as e:
    app.logger.critical('exception encountered while parsing the config file, see details below')
    app.logger.exception(e)
    sys.exit(1)

GLOBAL_CONF = config['global']  # load & export global configs

app = ConfigApp(app, config).load_config()  # load configurations to the app instance

db = SQLAlchemy(session_options={'autocommit': False})
db.init_app(app)

# requests session
session = requests.Session()
retry = Retry(total=10, backoff_factor=0.2,
              status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# initialize celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# register tasks
app.config['imports'] = app.config['CeleryTasks']

# we really need wild-card import here for now
from app.api.v1.routes import register_docs  # pylint: disable=wildcard-import


@app.after_request
def no_cache(response):
    """Make sure that API responses are not cached by setting headers."""
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    response.cache_control.max_age = 0
    response.headers['Pragma'] = 'no-cache'
    response.expires = 0
    return response


@app.after_request
def add_security_headers(response):
    """Make sure to add security headers to each API response."""
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    if app.config['STRICT_HTTPS']:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['SUPPORTED_LANGUAGES'])


register_docs()
