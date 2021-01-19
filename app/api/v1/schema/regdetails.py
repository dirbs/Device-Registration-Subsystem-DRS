"""
DRS Registration schema package.
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
from marshmallow import Schema, fields, validates, pre_load, pre_dump, post_dump, post_load, validate
from app.api.v1.helpers.validators import *
from app.api.v1.models.devicequota import DeviceQuota
from app.api.v1.models.status import Status
import ast
import pydash
from app import app, GLOBAL_CONF
from flask_babel import gettext as _


class RegistrationDetailsSchema(Schema):
    """Schema for Registration routes."""

    id = fields.Int(required=False)
    device_count = fields.Int(required=True, error_messages={'required': 'Device count is required'})
    reviewer_id = fields.Str(required=False)
    reviewer_name = fields.Str(required=False)
    report_allowed = fields.Boolean(required=False)
    user_id = fields.Str(required=True, error_messages={'required': 'User Id is required'})
    user_name = fields.Str(required=True, error_messages={'required': 'User Name is required'})
    imei_per_device = fields.Int(required=True, error_messages={'required': 'Imei per device count is required'})
    m_location = fields.Str(required=True, error_messages={'required': 'manufacturing location is a required field'})
    file = fields.Str(required=False)
    file_link = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    imeis = fields.List(fields.List(fields.Str(validate=validate_imei)), required=False)
    imeis_count = fields.Int(required=False)
    status_label = fields.Str(required=False)
    # processed = fields.Boolean()
    processing_status_label = fields.Str()
    report_status_label = fields.Str()
    tracking_id = fields.Str()
    report = fields.String()
    duplicate_imeis_file = fields.String(missing='')
    msisdn = fields.Str()
    network = fields.Str()

    @pre_load()
    def file_webpage(self, data):
        """Validates type of input."""
        if 'imeis' not in data and 'file' not in data:
            raise ValidationError('Either file or webpage input is required',
                                  field_names=['imeis', 'file']
                                  )
        elif 'imeis' in data and 'file' in data:
            raise ValidationError('Either file or webpage input is required',
                                  field_names=['imeis', 'file']
                                  )

    @pre_load()
    def convert_imei(self, data):
        """Converts imei to supported formats."""
        if 'imeis' in data and 'file' not in data:
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

    @pre_dump()
    def get_file_link(self, data):
        """Returns downloadable links to the files."""
        if not data.imeis:
            upload_dir_path = GLOBAL_CONF['upload_directory']
            data.file_link = '{server_dir}/{local_dir}/{file_name}'.format(
                                    server_dir=upload_dir_path,
                                    local_dir=data.tracking_id,
                                    file_name=data.file
                                )

    @pre_dump()
    def request_status(self, data):
        """Returns current status of the request."""
        data.status_label = Status.get_status_type(data.status)
        data.processing_status_label = Status.get_status_type(data.processing_status)
        data.report_status_label = Status.get_status_type(data.report_status)

    @pre_dump()
    def convert_imeis(self, data):
        """Convert imeis."""
        if data.imeis:
            try:
                data.imeis = ast.literal_eval(data.imeis)
            except:
                pass

    @pre_load()
    def create_device_quota(self, data):
        """Create a new device quotes for the user."""
        if 'user_id' in data:
            DeviceQuota.get_or_create(data['user_id'], 'importer')

    @validates('device_count')
    def validate_device_count(self, value):
        """Validates devices count."""
        if value <= 0:
            raise ValidationError('Device count must be a positive number',
                                  field_names=['device_count'])
        if value > 10000000:
            raise ValidationError('Device count in single request should be less than 10000000')

    @validates('m_location')
    def validate_manufacturing_location(self, value):
        """Validates manufacturing localtions."""
        locations = ['overseas', 'local']
        if value not in locations:
            raise ValidationError('Manufacturing location must be either local or overseas',
                                  field_names=['m_location'])

    @validates('file')
    def validate_filename(self, value):
        """Validates file name."""
        if not value.endswith('.tsv'):
            raise ValidationError('Only tsv files are allowed', field_names=['file'])
        elif len(value) > 100:
            raise ValidationError('File name length should be under 100 characters', field_names=['file'])

    @validates('user_id')
    def validate_user_id(self, value):
        """Validates user id."""
        validate_input('user id', value)

    @validates('user_name')
    def validate_user_name(self, value):
        """Validates user name."""
        validate_input('user name', value)
