"""
DRS De-Registration schema package.
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
from marshmallow import Schema, validates, ValidationError, pre_load, pre_dump
from marshmallow import fields
from app.api.v1.helpers.validators import *
from flask_babel import lazy_gettext as _

from app import app, GLOBAL_CONF
from app.api.v1.models.status import Status
from app.api.v1.models.devicequota import DeviceQuota


class DeRegDetailsSchema(Schema):
    """Schema for De-Registration Request Rout."""

    id = fields.Int(required=False)
    status_label = fields.Str(required=False)
    processing_status_label = fields.Str(required=False)
    report_status_label = fields.Str(required=False)
    device_count = fields.Int(required=True, error_messages={'required': 'device count is a required field'})
    reason = fields.Str(required=True, error_messages={'required': 'reason is a required field'})
    file = fields.Str(required=True, error_messages={'required': 'file is a required field'})
    file_link = fields.Str()
    user_id = fields.Str(required=True, error_messages={'required': 'User Id is required'})
    user_name = fields.Str(required=True, error_messages={'required': 'User Name is required'})
    reviewer_id = fields.Str(required=False)
    reviewer_name = fields.Str(required=False)
    report_allowed = fields.Boolean(required=False)
    tracking_id = fields.Str(required=False)
    report = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    invalid_imeis_file = fields.String(missing='')

    @pre_dump()
    def translate_status(self, data):
        """ Takes De-Registration details as input
            and translate codes for statuses and return the object. """

        data.status_label = Status.get_status_type(data.status)
        data.processing_status_label = Status.get_status_type(data.processing_status)
        data.report_status_label = Status.get_status_type(data.report_status)

    @pre_dump()
    def get_file_link(self, data):
        """Return file link."""
        upload_dir_path = GLOBAL_CONF['upload_directory']
        data.file_link = '{server_dir}/{local_dir}/{file_name}'.format(
                                server_dir=upload_dir_path,
                                local_dir=data.tracking_id,
                                file_name=data.file
                            )

    @validates('device_count')
    def validate_device_count(self, value):
        """ Validator method for validating device_count,
            to check if value is not negative. """

        if value <= 0:
            raise ValidationError('Device count must be a positive number',
                                  fields=['device_count'])

    @validates('file')
    def validate_filename(self, value):
        """ Validate file, restrict files other than txt
            and filename size grater than 100 characters. """

        if not value.endswith('.txt'):
            raise ValidationError('Only txt files are allowed', fields=['filename'])
        elif len(value) > 100:
            raise ValidationError('File name length should be under 100 characters', fields=['file'])

    @pre_load()
    def validate_reason(self, data):
        """ Validate reason for De-Registration. """

        if 'reason' in data:
            if len(data['reason']) == 0:
                raise ValidationError('Invalid reason', field_names=['reason'])

    @pre_load()
    def create_device_quota(self, data):
        """Create a new device quotes for the user."""
        if 'user_id' in data:
            DeviceQuota.get_or_create(data['user_id'], 'exporter')

    @validates('user_id')
    def validate_user_id(self, value):
        """ Validate user_id. """
        validate_input('user id', value)

    @validates('user_name')
    def validate_user_name(self, value):
        """ Validate user name. """
        validate_input('user name', value)
