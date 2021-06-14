"""
DRS Registration device schema package.
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

from app.api.v1.helpers.validators import *
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.devicetechnology import DeviceTechnology
from app.api.v1.models.technologies import Technologies
from app.api.v1.models.devicetype import DeviceType
from app.api.v1.models.status import Status
from flask_babel import lazy_gettext as _
from app import app, GLOBAL_CONF

class AssembledDevicesSchema(Schema):
    """Schema for Device Details."""

    parent_id = fields.Str(required=True)
    user_id = fields.Str(required=True, error_messages={'required': 'user_id is required'})
    device_count = fields.Str(required=True, error_messages={'required': 'Device count is required'})
    imei_per_device = fields.Str(required=True, error_messages={'required': 'Imei per device count is required'})
    file = fields.Str(required=False, error_messages={'required': 'Assembled Devices file is required'})

    @pre_load()
    def check_reg_id(self, data):
        """Validates request id."""
        reg_details_id = data['parent_id']
        reg_details = RegDetails.get_by_id(reg_details_id)

        if 'user_id' in data and reg_details.user_id != data['user_id']:
            raise ValidationError('Permission denied for this request', field_names=['user_id'])
        if not reg_details:
            raise ValidationError('The request id provided is invalid', field_names=['reg_id'])

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


    @validates('file')
    def validate_filename(self, value):
        """Validates file name."""
        if not value.endswith('.tsv'):
            raise ValidationError('Only tsv files are allowed', field_names=['file'])
        elif len(value) > 100:
            raise ValidationError('File name length should be under 100 characters', field_names=['file'])

    @validates('parent_id')
    def validate_parent_id(self, value):
        """Validates user id."""
        validate_digit_field('parent id', value)
        validate_input('parent id', value)

    @validates('user_id')
    def validate_user_id(self, value):
        """Validates user id."""
        validate_input('user id', value)

    @validates('device_count')
    def validate_device_count(self, value):
        """Validates user id."""
        validate_digit_field('device count', value)
        validate_input('device count', value)

    @validates('imei_per_device')
    def validate_imei_per_device(self, value):
        """Validates user id."""
        validate_digit_field('imei count', value)
        validate_input('imei count', value)

