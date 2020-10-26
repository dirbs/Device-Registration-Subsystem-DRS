"""
DRS De-Registration device schema package.
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
from app.api.v1.models.deregdetails import DeRegDetails
from app.api.v1.models.status import Status
from flask_babel import lazy_gettext as _


class DeRegDeviceSchema(Schema):
    """Schema for De-Registration Device routes."""

    id = fields.Int(required=False)
    model_name = fields.Str(required=True, error_messages={'required': 'model_name is a required field'})
    brand_name = fields.Str(required=True, error_messages={'required': 'brand_name is a required field'})
    model_num = fields.Str(required=True, error_messages={'required': 'model_number is a required field'})
    technology = fields.Str(required=True, error_messages={'required': 'r_interface is a required field'})
    device_type = fields.Str(required=True, error_messages={'required': 'device_type is a required field'})
    count = fields.Int(required=True, error_messages={'required': 'count is a required field'})
    operating_system = fields.Str(required=True, error_messages={'required': 'operating_system is a required field'})
    tac = fields.Str(required=True, error_messages={'required': 'tac is a required field'})
    deregdetail_id = fields.Int(required=False)

    @pre_dump()
    def tranform_data(self, data):
        """Transform request data."""
        data.count = data.device_count
        data.brand_name = data.brand


class DeRegRequestSchema(Schema):
    """Schema for De-Reg request."""
    devices = fields.List(fields.Nested(DeRegDeviceSchema), required=True)
    user_id = fields.Str(required=True, error_messages={'required': 'User Id is required'})

    @pre_load()
    def check_reg_id(self, data):
        """Validates registration id."""
        dereg_details_id = data['dereg_id']
        dereg_details = DeRegDetails.get_by_id(dereg_details_id)
        if not dereg_details:
            raise ValidationError('The request id provided is invalid', field_names=['dereg_id'])
        if 'user_id' in data and data['user_id'] != dereg_details.user_id:
            raise ValidationError('Permission denied for this request', field_names=['user_id'])
        else:
            status = Status.get_status_type(dereg_details.status)
            if status != 'New Request':
                raise ValidationError(_('This step can only be performed for New Request'), field_names=['status'])


class DeRegRequestUpdateSchema(Schema):
    """Schema for updating De-Registration request."""

    update_restricted = ['In Review', 'Approved', 'Rejected', 'Closed', 'New Request', 'Awaiting Documents']
    devices = fields.List(fields.Nested(DeRegDeviceSchema), required=True)
    user_id = fields.Str(required=True, error_messages={'required': 'User Id is required'})

    @pre_load()
    def check_reg_id(self, data):
        """Validates ID of the request."""
        dereg_details_id = data['dereg_id']
        dereg_details = DeRegDetails.get_by_id(dereg_details_id)
        if not dereg_details:
            raise ValidationError('The request id provided is invalid', field_names=['dereg_id'])
        if 'user_id' in data and data['user_id'] != dereg_details.user_id:
            raise ValidationError('Permission denied for this request', field_names=['user_id'])
        else:
            status = Status.get_status_type(dereg_details.status)
            if status in self.update_restricted:
                raise ValidationError('Update is restricted for request in status {0}'.format(status),
                                      field_names=['status'])
