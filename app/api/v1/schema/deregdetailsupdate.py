"""
DRS De-Registration update schema package.
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
from marshmallow import Schema, validates, ValidationError, pre_load, pre_dump
from marshmallow import fields
from app.api.v1.helpers.validators import *
from app.api.v1.models.status import Status
from app.api.v1.models.devicequota import DeviceQuota
from app.api.v1.models.deregdetails import DeRegDetails
from flask_babel import _


class DeRegDetailsUpdateSchema(Schema):
    """Schema for De-Registration request update route."""

    update_restricted = ['In Review', 'Approved', 'Rejected', 'Closed', 'Awaiting Documents']
    closed_restricted = ['In Review', 'Approved', 'Rejected']

    id = fields.Int(required=False)
    status_label = fields.Str(required=False)
    processing_status_label = fields.Str(required=False)
    report_status_label = fields.Str(required=False)
    device_count = fields.Int(required=False, error_messages={'required': 'device count is a required field'})
    reason = fields.Str(required=False, error_messages={'required': 'reason is a required field'})
    file = fields.Str(required=False, error_messages={'required': 'file is a required field'})
    user_id = fields.Str(required=True, error_messages={'required': 'User Id is required'})
    user_name = fields.Str(required=False)
    reviewer_id = fields.Str(required=False)
    reviewer_name = fields.Str(required=False)
    tracking_id = fields.Str(required=False)
    invalid_imeis_file = fields.String(missing='')

    @pre_load()
    def check_file_device_count(self, data):
        """ Validate if dependent fields, file and device count are present. """

        file_in_data = True if 'file' in data else False
        d_count_in_data = True if 'device_count' in data else False
        if file_in_data != d_count_in_data:
            raise ValidationError('File and device_count are dependent fields.', field_names=['file', 'device_count'])

    @pre_load()
    def check_valid_dereg_details(self, data):
        """ Validate the De-Registration ID. """

        if 'status' not in data:
            raise ValidationError('The De-Registration id does not exists',
                                  field_names=['error'])

    @pre_load()
    def update_allow(self, data):
        """ This method translates statuses from codes to user readable texts.
            It checks if the request can be updated or is it update restricted. """

        status = Status.get_status_type(data['status'])
        report_status = Status.get_status_type(data['report_status'])
        processing_status = Status.get_status_type(data['processing_status'])

        if 'close_request' in data:
            if status == 'Closed':
                raise ValidationError(_('The request status is already Closed').format(_(status)),
                                      field_names=['message'])
            elif status in self.closed_restricted:
                raise ValidationError(_('The request status is %(status)s, which cannot be Closed', status=_(status)),
                                      field_names=['message'])
        elif processing_status == 'Processing' or report_status == 'Processing':
            raise ValidationError(_('The request is in Progress, which cannot be updated'),
                                  field_names=['status'])
        elif status in self.update_restricted:
            raise ValidationError(_('The request status is %(status)s, which cannot be updated', status=_(status)),
                                  field_names=['status'])
        elif status == 'New Request' and 'file' in data:
            raise ValidationError(_('The request status is %(status)s, which cannot be updated', status=_(status)),
                                  field_names=['status'])
        elif status == 'New Request' and 'reason' in data:
            raise ValidationError(_('The request status is %(status)s, which cannot be updated', status=_(status)),
                                  field_names=['reason'])

    @pre_dump()
    def translate_status(self, data):
        """Translates statuses of request."""
        data.status_label = Status.get_status_type(data.status)
        data.processing_status_label = Status.get_status_type(data.processing_status)
        data.report_status_label = Status.get_status_type(data.report_status)

    @validates('device_count')
    def validate_device_count(self, value):
        """Validates current device count."""
        if value <= 0:
            raise ValidationError('Device count must be a positive number',
                                  fields=['device_count'])

    @validates('file')
    def validate_filename(self, value):
        """Validates name of the file."""
        if not value.endswith('.txt'):
            raise ValidationError('Only txt files are allowed', fields=['filename'])
        elif len(value) > 100:
            raise ValidationError('File name length should be under 100 characters', fields=['file'])

    @pre_load()
    def validate_reason(self, data):
        """Validate reason field in request."""
        if 'reason' in data:
            if len(data['reason']) == 0:
                raise ValidationError('Invalid reason', field_names=['reason'])

    @pre_load()
    def check_permissions(self, data):
        """Check if user have permission for this request."""
        reg_details = DeRegDetails.get_by_id(data['dereg_id'])
        request_user = reg_details.user_id
        if 'user_id' in data and data['user_id'] != request_user:
            raise ValidationError('Permission denied for this request', field_names=['user_id'])
