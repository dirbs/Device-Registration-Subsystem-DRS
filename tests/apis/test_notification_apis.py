"""
module for common apis test

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
import json

from app.api.v1.models.notification import Notification

# api urls
NOTIFICATION_API = 'api/v1/notification'


def test_with_no_notification_data_in_table(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the notification api return empty response when no data in table."""
    user_id = 'abc-user'
    api_url = '{api}?user_id={user_id}'.format(api=NOTIFICATION_API, user_id=user_id)
    rv = flask_app.get(api_url)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('notifications') == []


def test_with_empty_user_id(flask_app):
    """Verify that the api responds correctly on wrong/empty input data."""
    # test with empty user id
    user_id = ''
    api_url = '{api}?user_id={user_id}'.format(api=NOTIFICATION_API, user_id=user_id)
    rv = flask_app.get(api_url)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('error')[0] == 'user_id cannot be empty'

    # test with no user_id param
    rv = flask_app.get(NOTIFICATION_API)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('error')[0] == 'user_id cannot be empty'


def test_with_existing_notification_data(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the api responds correctly when notification data exists in table."""
    # generate a  registration request type notification
    user_id = 'test-user1'
    notification = Notification(user_id=user_id, request_id=1342, request_type='registration_request',
                                request_status=6, message='a test notification has been generated')
    notification.add()

    # get notification for user id = test-user1
    api_url = '{api}?user_id={user_id}'.format(api=NOTIFICATION_API, user_id=user_id)
    rv = flask_app.get(api_url)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert len(data.get('notifications')) == 1
    data = data.get('notifications')[0]
    assert data.get('request_id') == 1342
    assert data.get('request_status') == 6
    assert data.get('request_type') == 'registration_request'
    assert data.get('id') == 1
    assert data.get('message') == 'a test notification has been generated'

    # generate multiple notifications for the same user
    notification = Notification(user_id=user_id, request_id=1343, request_type='de_registration_request',
                                request_status=7, message='a test notification has been generated')
    notification.add()
    api_url = '{api}?user_id={user_id}'.format(api=NOTIFICATION_API, user_id=user_id)
    rv = flask_app.get(api_url)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    assert len(data.get('notifications')) == 2


def test_mark_notification_as_read_api(flask_app, db):  # pylint: disable=unused-argument
    """Verify that a generated notification is not return when mark as read."""
    # generate a  registration request type notification
    user_id = 'test-user1'
    notification = Notification(user_id=user_id, request_id=1342, request_type='registration_request',
                                request_status=6, message='a test notification has been generated')
    notification.add()

    api_url = '{api}?user_id={user_id}'.format(api=NOTIFICATION_API, user_id=user_id)
    rv = flask_app.get(api_url)
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    notification_id = data['notifications'][0]['id']

    # mark notification as read
    body_data = {'notification_id': notification_id, 'user_id': user_id}
    headers = {'Content-Type': 'application/json'}
    rv = flask_app.put(NOTIFICATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 201


def test_notification_put_api_with_invalid_data(flask_app, db):  # pylint: disable=unused-argument
    """Verify that the notification put api responds correctly in case of invalid input."""
    # invalid user id
    user_id = 'abcd-user'
    body_data = {'notification_id': 2, 'user_id': user_id}
    headers = {'Content-Type': 'application/json'}
    rv = flask_app.put(NOTIFICATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 400
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('error')[0] == 'user {0} does not exists'.format(user_id)

    # generate a notification with the same user id
    notification = Notification(user_id=user_id, request_id=1342, request_type='registration_request',
                                request_status=6, message='a test notification has been generated')
    notification.add()

    # invalid notification id test
    notification_id = 35
    body_data = {'notification_id': notification_id, 'user_id': user_id}
    rv = flask_app.put(NOTIFICATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 400
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('error')[0] == 'notification {0} does not exists'.format(notification_id)

    # wrong user for notification test
    user_id_2 = 'test-user1'
    notification = Notification(user_id=user_id_2, request_id=13, request_type='registration_request',
                                request_status=6, message='a test notification has been generated')
    notification.add()

    # get notification id
    rv = flask_app.get('{0}?user_id={1}'.format(NOTIFICATION_API, user_id_2))
    assert rv.status_code == 200
    data = json.loads(rv.data.decode('utf-8'))
    notification_id = data['notifications'][0]['id']

    # try to mark notification as read with wrong user
    body_data = {'notification_id': notification_id, 'user_id': user_id}
    rv = flask_app.put(NOTIFICATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 400
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('error')[0] == 'invalid user id'

    # string arguments test
    body_data = {'notification_id': '', 'user_id': ''}
    rv = flask_app.put(NOTIFICATION_API, data=json.dumps(body_data), headers=headers)
    assert rv.status_code == 422
    data = json.loads(rv.data.decode('utf-8'))
    assert data['notification_id'][0] == "Bad 'notification_id':'' argument format. Accepts only integer"


def test_post_method_not_allowed(flask_app):
    """Verify that POST method is not allowed on config/server-configs apis."""
    rv = flask_app.post(NOTIFICATION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'


def test_delete_method_not_allowed(flask_app):
    """Verify that DELETE method is not allowed on config/server-configs apis."""
    rv = flask_app.delete(NOTIFICATION_API)
    assert rv.status_code == 405
    data = json.loads(rv.data.decode('utf-8'))
    assert data.get('message') == 'method not allowed'
