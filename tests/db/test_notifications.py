"""
Notification Model Unittests

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
from sqlalchemy import text

from tests._helpers import get_notification_id, get_single_notification, get_user_notifications, exists_notification, \
    exists_user_notifications, delete_user_notifications
from app.api.v1.models.notification import Notification


# noinspection PyUnusedLocal,PyShadowingNames
def test_add_notification(db, session):  # pylint: disable=unused-argument
    """Verify that the notifications model add functionality works correctly."""
    # add a notification using model
    user_id = 'test-user'
    request_id = 213
    request_type = 'registration'
    request_status = 3
    message = 'this is a test notification'
    notification = Notification(user_id=user_id, request_id=request_id, request_type=request_type,
                                request_status=request_status, message=message)
    notification.add()

    # check entry in database
    res = session.execute(text("""SELECT * FROM public.notification
                                    WHERE request_id='213'""")).fetchone()
    assert res.user_id == user_id
    assert res.request_id == request_id
    assert res.request_type == request_type
    assert res.request_status == 3
    assert res.message == message
    # marked_read should be false initially
    assert not res.marked_read

    # notification is not added without committing to the db using add()
    user_id = 'test-user'
    request_id = 2100
    request_type = 'de_registration'
    request_status = 7
    message = 'this is a test notification'
    notification = Notification(user_id=user_id, request_id=request_id, request_type=request_type,
                                request_status=request_status, message=message)
    res = session.execute(text("""SELECT * FROM public.notification
                                    WHERE request_id='2100'""")).fetchone()
    assert not res


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
# noinspection PyUnusedLocal,PyShadowingNames
def test_exist_users(db, session):  # pylint: disable=unused-argument
    """Verify that the exist_user() work correctly."""
    # add a notification for user
    user_id = 'notf-user'
    request_id = 223
    request_type = 'registration'
    request_status = 3
    message = 'this is a test notification'
    notification = Notification(user_id=user_id, request_id=request_id, request_type=request_type,
                                request_status=request_status, message=message)
    notification.add()
    user_exists_bool = Notification.exist_users(user_id)

    # check if it really exists in db
    res = exists_user_notifications(session, user_id)
    assert res is user_exists_bool

    # remove the above notification and then check again
    assert delete_user_notifications(session, user_id)
    user_exists_bool = Notification.exist_users(user_id)
    res = exists_user_notifications(session, user_id)
    assert res is user_exists_bool


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
# noinspection PyUnusedLocal,PyShadowingNames
def test_exists(db, session):  # pylint: disable=unused-argument
    """Verify that exists() responds correctly while checking for existence of notifications."""
    # add a new notification
    user_id = 'notf-user'
    request_id = 224
    request_type = 'registration'
    request_status = 7
    message = 'this is a test notification'
    notification = Notification(user_id=user_id, request_id=request_id, request_type=request_type,
                                request_status=request_status, message=message)
    notification.add()

    # get notification id
    notification_id = get_notification_id(session, request_id)
    notification_bool = Notification.exists(notification_id)

    # check if it really exists
    res = exists_notification(session, notification_id)
    assert res is notification_bool


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
# noinspection PyUnusedLocal,PyShadowingNames
def test_get(db, session):  # pylint: disable=unused-argument
    """Verify that the get() returns correct results as expected."""
    # get from method for notf-user
    user_id = 'notf-user'
    method_res = Notification.get(user_id)
    query_res = get_user_notifications(session, user_id)  # check if the results are really same
    assert len(query_res) == len(method_res)


# noinspection PyUnusedLocal,PyShadowingNames
def test_get_single(db, session):  # pylint: disable=unused-argument
    """Verify that the get_single() returns correct results as expected
    from database table.
    """
    # add a notification for user
    user_id = 'notf-user'
    request_id = 225
    request_type = 'registration'
    request_status = 3
    message = 'this is a test notification'
    notification = Notification(user_id=user_id, request_id=request_id, request_type=request_type,
                                request_status=request_status, message=message)
    notification.add()
    notification_id = get_notification_id(session, request_id)
    notification_data = Notification.get_single(notification_id)
    notification_data_raw = get_single_notification(session, notification_id)

    # verify results of both
    assert notification_data_raw.id == notification_data.id
    assert notification_data_raw.user_id == notification_data.user_id
    assert notification_data_raw.request_id == notification_data.request_id
    assert notification_data_raw.request_status == notification_data.request_status
    assert notification_data_raw.message == notification_data.message


# noinspection PyUnusedLocal,PyShadowingNames
def test_mark_read(db, session):  # pylint: disable=unused-argument
    """Verify that mark_read() mark marked_read column as True."""
    # add a notification
    user_id = 'notf-user'
    request_id = 226
    request_type = 'registration'
    request_status = 3
    message = 'this is a test notification'
    notification = Notification(user_id=user_id, request_id=request_id, request_type=request_type,
                                request_status=request_status, message=message)
    notification.add()

    # get notification id
    notification_id = get_notification_id(session, request_id)
    notification_data = get_single_notification(session, notification_id)
    assert notification_data.marked_read is False

    # call mark_read()
    Notification.mark_read(notification_id)
    notification_data = get_single_notification(session, notification_id)
    assert notification_data.marked_read is True
