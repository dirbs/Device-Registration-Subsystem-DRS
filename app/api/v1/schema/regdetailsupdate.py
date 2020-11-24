"""
DRS Registration update schema package.
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
from marshmallow import Schema, fields, validates, ValidationError, pre_load, pre_dump
import ast
import pydash

from app.api.v1.helpers.validators import *
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.devicequota import DeviceQuota
from app.api.v1.models.status import Status
from flask_babel import lazy_gettext as _


class RegistrationDetailsUpdateSchema(Schema):
    """Schema for Registration update routes."""

    update_restricted = ['In Review', 'Approved', 'Rejected', 'Closed', 'New Request', 'Awaiting Documents']
    closed_restricted = ['In Review', 'Approved', 'Rejected']

    id = fields.Str(required=False)
    tracking_id = fields.Str(required=False)
    device_count = fields.Int(required=False)
    user_id = fields.Str(required=True, error_messages={'required': 'User Id is required'})
    user_name = fields.Str(required=False)
    reviewer_id = fields.Str(required=False)
    reviewer_name = fields.Str(required=False)
    imei_per_device = fields.Int(required=False)
    m_location = fields.Str(required=False)
    file = fields.Str(required=False)
    imeis = fields.List(fields.List(fields.Str(validate=validate_imei)), required=False)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    imeis_count = fields.Int(required=False)
    status_label = fields.Str(required=False)
    processing_status_label = fields.Str()
    report_status_label = fields.Str()
    close_request = fields.Boolean(required=False)
    duplicate_imeis_file = fields.String(missing='')

    @pre_load()
    def file_webpage(self, data):
        """Validates type of input."""
        imeis_required = 'device_count' in data or 'imei_per_device' in data
        imei_input_info_required = 'imeis' in data or 'file' in data

        if imeis_required:
            if 'imeis' not in data and 'file' not in data:
                raise ValidationError('Either file or webpage input is required',
                                      field_names=['imeis', 'file']
                                      )
            elif 'imeis' in data and 'file' in data:
                raise ValidationError('Either file or webpage input is required',
                                      field_names=['imeis', 'file']
                                      )

        if imei_input_info_required:
            if 'device_count' not in data:
                raise ValidationError('Device count is a required when in case of file or wepage input',
                                      field_names=['device_count']
                                      )
            elif 'imei_per_device' not in data:
                raise ValidationError('Imeis per device is a required when in case of file or wepage input',
                                      field_names=['imei_per_device']
                                      )

    @pre_load()
    def update_allow(self, data):
        """Check if current request is allowed to update."""
        status = Status.get_status_type(data['status'])
        processing_status = Status.get_status_type(data['processing_status'])
        report_status = Status.get_status_type(data['report_status'])

        if 'close_request' in data:
            if status == 'Closed':
                raise ValidationError(_('The request status is already Closed'),
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


    @pre_load()
    def check_permissions(self, data):
        """Validates user permissions."""
        reg_details = RegDetails.get_by_id(data['reg_id'])
        request_user = reg_details.user_id
        if 'user_id' in data and data['user_id'] != request_user:
            raise ValidationError('Permission denied for this request.', field_names=['user_id'])
        if 'imeis' in data:
            if not reg_details.imeis or reg_details.imeis == 'None':
                raise ValidationError('Input type cannot be updated, Require file',
                                      field_names=['file']
                                      )
        elif 'file' in data:
            if not reg_details.file or reg_details.file == 'None':
                raise ValidationError('Input type cannot be updated, Require Imeis',
                                      field_names=['imeis']
                                      )

    @pre_dump()
    def post_process_imei(self, registration_detail):
        """Process imies after processing."""
        if registration_detail.imeis:
            registration_detail.imeis = ast.literal_eval(registration_detail.imeis)
        registration_detail.status_label = Status.get_status_type(registration_detail.status)
        registration_detail.processing_status_label = Status.get_status_type(registration_detail.processing_status)
        registration_detail.report_status_label = Status.get_status_type(registration_detail.report_status)

    @pre_load()
    def convert_imei(self, data):
        """Convert imeis to supported format."""
        if 'imeis' in data:
            try:
                data['imeis'] = ast.literal_eval(data.get('imeis'))
            except Exception as e:
                raise ValidationError('Invalid format for IMEIs Input', field_names=['imeis'])
            imeis = pydash.flatten_deep(data['imeis'])
            if len(imeis) == 0:
                raise ValidationError('Invalid format for IMEIs Input', field_names=['imeis'])
            elif not isinstance(data['imeis'][0], list):
                raise ValidationError('Invalid format for IMEIs Input', field_names=['imeis'])
            elif len(imeis) != len(list(set(imeis))):
                raise ValidationError(_('Duplicate IMEIs in request'), field_names=['imeis'])
            elif 'device_count' in data and data['device_count'].isdigit():
                if int(data['device_count']) > 10:
                    raise ValidationError('Only 10 device are allowed in case of webpage input',
                                          field_names=['imeis'])
                if int(data['device_count']) != len(data['imeis']):
                    raise ValidationError('Device count should be same as no of devices',
                                          field_names=['device_count'])
            if 'imei_per_device' in data and data['imei_per_device'].isdigit():
                if int(data['imei_per_device']) > 5:
                    raise ValidationError('Only 5 imeis are allowed per device in webpage',
                                          field_names=['imei_per_device'])
                invalid = list(filter(lambda x: len(x) != int(data['imei_per_device']), data['imeis']))
                if len(invalid) > 0:
                    raise ValidationError('No of imei for each device should be same as imei per device',
                                          field_names=['imei_per_device'])

    @validates('device_count')
    def validate_device_count(self, value):
        """Validates device count."""
        if value <= 0:
            raise ValidationError('Device count must be a positive number',
                                  field_names=['device_count'])
        if value > 10000000:
            raise ValidationError('Device count in single request should be less than 10000000')

    @validates('imei_per_device')
    def validate_imei_per_device(self, value):
        """Validates imeis per device count."""
        if value <= 0 or value > 5:
            raise ValidationError('Imei per device must be in range of 1 to 5',
                                  field_names=['imei_per_device'])

    @validates('m_location')
    def validate_manufacturing_location(self, value):
        """Validates manufacturing location of the device."""
        locations = ['overseas', 'local']
        if value not in locations:
            raise ValidationError('Manufacturing location must be either local or overseas',
                                  field_names=['m_location'])

    @validates('file')
    def validate_filename(self, value):
        """Validates filenames."""
        if not value.endswith('.tsv'):
            raise ValidationError('Only tsv files are allowed', field_names=['file'])

