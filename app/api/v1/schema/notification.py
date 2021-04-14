"""
DRS notification schema package.
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
from marshmallow import Schema, fields


class NotificationGetArgs(Schema):
    """Args schema for notifications GET route."""

    user_id = fields.String(required=True, description='Id of the user', missing='')

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class NotificationPutArgs(Schema):
    """Args schema for notifications PUT route."""

    user_id = fields.String(required=True, description='Id of the user')
    notification_id = fields.Integer(required=True, description='Id of the notification')

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class Notification(Schema):
    """Response schema for notification response."""

    id = fields.Integer(required=True, description='Id of the notification')
    request_id = fields.Integer(required=True, description='Id of the request to which notification is')
    request_type = fields.String(required=True, description='Type of the request')
    request_status = fields.Integer(required=True, description='status of the current request')
    message = fields.String(required=True, description='notification message')
    generated_at = fields.DateTime(required=True, description='Time-stamp on which notification is generated at')


class Notifications(Schema):
    """Response schema for notifications route."""

    notifications = fields.List(fields.Nested(Notification, required=True), required=False)
