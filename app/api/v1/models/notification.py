"""
DRS Notification Model package.
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
from app import db
from sqlalchemy.sql import exists
from sqlalchemy import desc


class Notification(db.Model):
    """Model class for notification table."""

    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False)
    request_id = db.Column(db.Integer, nullable=False)
    request_type = db.Column(db.String(24), nullable=False)
    request_status = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(120), nullable=True)
    marked_read = db.Column(db.Boolean, default=False)
    generated_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, user_id, request_id, request_type, request_status, message=''):
        """Constructor"""
        self.user_id = user_id
        self.request_id = request_id
        self.request_type = request_type
        self.request_status = request_status
        self.message = message
        self.marked_read = False

    def add(self):
        """Method to add a notification"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @staticmethod
    def exist_users(user_id):
        """Method to check if notifications for a user exists."""
        return db.session.query(exists().where(Notification.user_id == user_id)).scalar()

    @staticmethod
    def exists(notification_id):
        """Method to check if a notification exists."""
        return db.session.query(exists().where(Notification.id == notification_id)).scalar()

    @staticmethod
    def get(user_id):
        """Get all notifications for a user."""
        return Notification.query.order_by(desc(Notification.generated_at))\
            .filter_by(user_id=user_id).filter_by(marked_read=False).all()

    @staticmethod
    def get_single(notification_id):
        """Get a notification based on id."""
        return Notification.query.filter_by(id=notification_id).first()

    @staticmethod
    def mark_read(notification_id):
        """Method to mark a notification as read."""
        try:
            notification = Notification.query.filter_by(id=notification_id).first()
            notification.marked_read = True
            db.session.add(notification)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception
