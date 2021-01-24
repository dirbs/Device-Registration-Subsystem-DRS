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
    """Schema for USSD Registration routes."""
    cnic = fields.Int(required=True)
    msisdn = fields.Int(required=True)
    network = fields.Str(required=True)
    imeis = fields.List(fields.List(fields.Str(validate=validate_imei)), required=False)
    device_count = fields.Int(required=True, error_messages={'required': 'Device count is required'})

    @pre_load()
    def valid_imeis(self, data):
        if 'imeis' in data:
            try:
                imeis = data.get('imeis')[0]
                for individual_imei in imeis:
                    if individual_imei.isdigit() and (len(individual_imei) > 13) and (len(individual_imei) < 17):
                        pass
                    else:
                        raise ValidationError("IMEI must be digits only and between 14 and 16 characters long.", field_names=['imeis'])
            except Exception as e:
                raise ValidationError(str(e), field_names=['imeis'])

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
    def request_status(self, data):
        """Returns current status of the request."""
        data.status_label = Status.get_status_type(data.status)
        data.processing_status_label = Status.get_status_type(data.processing_status)
        data.report_status_label = Status.get_status_type(data.report_status)

    @validates('device_count')
    def validate_device_count(self, value):
        """Validates devices count."""
        if value <= 0:
            raise ValidationError('Device count must be a positive number',
                                  field_names=['device_count'])
        if value > 10000000:
            raise ValidationError('Device count in single request should be less than 10000000')

    @validates('network')
    def validate_network(self, value):
        """Validates network"""
        if value.isdigit():
            raise ValidationError('Network type should be a string',
                                  field_names=['network'])

class UssdTrackingSchema(Schema):
    """Schema for USSD Tracking."""
    msisdn = fields.Int(required=True)
    network = fields.Str(required=True)
    device_id = fields.Int(required=True)

    @pre_dump()
    def request_status(self, data):
        """Returns current status of the request."""
        data.status_label = Status.get_status_type(data.status)
        data.processing_status_label = Status.get_status_type(data.processing_status)
        data.report_status_label = Status.get_status_type(data.report_status)

    @validates('network')
    def validate_network(self, value):
        """Validates network"""
        if value.isdigit():
            raise ValidationError('Network type should be a string',
                                  field_names=['network'])

class UssdDeleteSchema(Schema):
    """Schema for USSD Tracking."""
    msisdn = fields.Int(required=True)
    network = fields.Str(required=True)
    device_id = fields.Int(required=True)
    close_request = fields.Str(required=True)


class UssdCountSchema(Schema):
    """Schema for USSD Tracking."""
    msisdn = fields.Int(required=True)
    network = fields.Str(required=True)
