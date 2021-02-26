"""
module for miscellaneous tests related to apis

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


def test_security_headers_on_apis(flask_app):
    """Verify that the security headers are present on API responses."""
    rv = flask_app.get('api/v1/')
    headers = rv.headers
    assert headers.get('X-Frame-Options') == 'DENY'
    assert headers.get('X-Content-Type-Options') == 'nosniff'


def test_cache_control_headers_on_apis(flask_app):
    """Verify that the cache control headers are present on API responses."""
    rv = flask_app.get('api/v1/')
    headers = rv.headers
    assert headers.get('Cache-Control')
    assert headers.get('Pragma') == 'no-cache'


def test_strict_https_header(flask_app, app):
    """Verify that the server include strict https header in api responses when enable."""
    app.config['STRICT_HTTPS'] = True  # enable strict https
    rv = flask_app.get('api/v1/')
    headers = rv.headers
    assert headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
    app.config['STRICT_HTTPS'] = False  # disable
    rv = flask_app.get('api/v1/')
    headers = rv.headers
    assert not headers.get('Strict-Transport-Security')
