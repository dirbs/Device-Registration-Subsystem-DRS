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


class DeviceDetailsSchema(Schema):
    """Schema for Device Details."""

    id = fields.Str(required=False)
    reg_details_id = fields.Int(required=True, error_messages={'required': 'Request id is required',
                                                               'invalid': 'Invalid reg_details_id'})
    brand = fields.Str(required=True, error_messages={'required': 'Brand is required'})
    model_name = fields.Str(required=True, error_messages={'required': 'Model name is required'})
    model_num = fields.Str(required=True, error_messages={'required': 'Model number is required'})
    operating_system = fields.Str(required=True, error_messages={'required': 'Operating system is required'})
    device_type = fields.Str(required=True, error_messages={'required': 'Device type is required'})
    technologies = fields.List(fields.Str(), required=True)
    user_id = fields.Str(required=True, error_messages={'required': 'user_id is required'})

    @pre_dump()
    def serialize_data(self, data):
        """Serializes/transforms data before dumping."""
        technologies_list = []
        if data.device_technologies:
            technologies = DeviceTechnology.get_device_technologies(data.id)
            for tech in technologies:
                tech_type = Technologies.get_technology_by_id(tech.technology_id)
                technologies_list.append(tech_type)
        data.technologies = technologies_list
        if data.device_types_id:
            device_type = DeviceType.get_device_type_by_id(data.device_types_id)
            data.device_type = device_type

    @pre_load()
    def check_reg_id(self, data):
        """Validates request id."""
        reg_details_id = data['reg_details_id']
        reg_details = RegDetails.get_by_id(reg_details_id)

        if 'user_id' in data and reg_details.user_id != data['user_id']:
            raise ValidationError('Permission denied for this request', field_names=['user_id'])
        if not reg_details:
            raise ValidationError('The request id provided is invalid', field_names=['reg_id'])
        else:
            status = Status.get_status_type(reg_details.status)
            if status != 'New Request':
                raise ValidationError(_('This step can only be performed for New Request'), field_names=['status'])

    @pre_load()
    def pre_process_technologies(self, data):
        """Assigns technologies."""
        if 'technologies' in data:
            validate_input('technologies', data['technologies'])
            data['technologies'] = data['technologies'].split(',')

    @validates('brand')
    def validate_brand(self, value):
        """Validates device brand."""
        validate_input('brand', value)

    @validates('model_name')
    def validate_model_name(self, value):
        """Validates device model name."""
        validate_input('model name', value)

    @validates('technologies')
    def validate_technologies(self, values):
        """Validate device technologies."""
        allowed_tech = Technologies.get_technologies_names()
        for value in values:
            if value not in allowed_tech:
                raise ValidationError("Radio Access Technology can be {0} only".format(','.join(allowed_tech)),
                                      fields=['technologies'])

    @validates('model_num')
    def validate_model_num(self, value):
        """Validates device model number."""
        validate_input('model number', value)

    @validates('operating_system')
    def validate_operating_system(self, value):
        """Validates device operating system."""
        validate_input('operating system', value)

