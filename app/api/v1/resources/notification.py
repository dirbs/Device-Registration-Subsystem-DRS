"""
DRS notification resource package.
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
from flask import Response
from flask_apispec import marshal_with, doc, MethodResource, use_kwargs

from app.api.v1.models.notification import Notification as NotificationModel
from app.api.v1.schema.notification import NotificationGetArgs, NotificationPutArgs, Notifications
from app.api.v1.schema.reviewer import ErrorResponse


class Notification(MethodResource):
    """Class for managing notification routes handler."""

    @doc(description='Get all notifications generated for a user', tags=['Notifications'])
    @marshal_with(Notifications, code=200, description='On success (Successful response)')
    @marshal_with(ErrorResponse, code=422, description='On Error (Invalid arguments format)')
    @marshal_with(ErrorResponse, code=500, description='On Error (Un-identified error)')
    @use_kwargs(NotificationGetArgs().fields_dict, locations=['query'])
    def get(self, **kwargs):
        """Get method handler for notification route."""
        user_id = kwargs.get('user_id')
        if user_id:
            notifications = NotificationModel.get(user_id)
            response = Notifications().dump(dict(notifications=notifications)).data
            return Response(json.dumps(response), status=200, mimetype='application/json')
        else:
            err = {'error': ['user_id cannot be empty']}
            return Response(json.dumps(ErrorResponse().dump(err).data),
                            status=422, mimetype='application/json')

    @doc(description='Mark a notification as read', tags=['Notifications'])
    @marshal_with(None, code=201, description='On success (operation successful)')
    @marshal_with(ErrorResponse, code=422, description='On Error (Invalid argument formats)')
    @marshal_with(ErrorResponse, code=400, description='On Error (Content not exists)')
    @marshal_with(ErrorResponse, code=500, description='On Error (Un-identified error)')
    @use_kwargs(NotificationPutArgs().fields_dict, locations=['json'])
    def put(self, **kwargs):
        """Put method handler for notification route."""
        user_id = kwargs.get('user_id')
        notification_id = kwargs.get('notification_id')

        if NotificationModel.exist_users(user_id):
            if NotificationModel.exists(notification_id):
                notification = NotificationModel.get_single(notification_id)
                if notification.user_id == user_id:
                    NotificationModel.mark_read(notification_id)
                    return Response(status=201, mimetype='application/json')
                else:
                    res = {'error': ['invalid user id']}
                    return Response(json.dumps(ErrorResponse().dump(res).data), status=400, mimetype='application/json')
            else:
                res = {'error': ['notification {id} does not exists'.format(id=notification_id)]}
                return Response(json.dumps(ErrorResponse().dump(res).data), status=400, mimetype='application/json')
        else:
            res = {'error': ['user {id} does not exists'.format(id=user_id)]}
            return Response(json.dumps(ErrorResponse().dump(res).data), status=400, mimetype='application/json')
