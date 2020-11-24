"""
DRS Registration resource package.
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

import re
from marshmallow import Schema, fields, validates, ValidationError
from app import GLOBAL_CONF


class AssociateImeisSchema(Schema):
    """Schema for IMEI association/de-association."""

    imei = fields.String(required=True, description='Device IMEI', error_messages={'required': 'imei is required'})
    uid = fields.String(required=True, description='UID', error_messages={'required': 'uid is required'})

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields

    @validates('imei')
    def _validate_imei(self, value):
        """Validator to validate IMEI field."""
        if len(value) < GLOBAL_CONF.get('min_imei_length'):
            raise ValidationError("IMEI is invalid", fields=['imei'])
        if len(value) > GLOBAL_CONF.get('max_imei_length'):
            raise ValidationError("IMEI is invalid", fields=['imei'])

    @validates('uid')
    def _validate_uid(self, value):
        """Validator to validate uid field."""
        if len(value) == 0:
            raise ValidationError("UID is invalid", fields=['uid'])
        match = re.match('^[a-zA-Z0-9\x2d]{10,20}$', value)
        if match is None:
            raise ValidationError("UID format is invalid", fields=['uid'])


class AssociateDuplicateImeisSchema(Schema):
    """Schema for duplicate IMEI association."""

    imei = fields.String(required=True, description='Device IMEI', error_messages={'required': 'imei is required'})
    uid = fields.String(required=True, description='UID', error_messages={'required': 'uid is required'})
    choice = fields.Boolean(required=True, description='user choice', error_messages={'required': 'choice is required'})


    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields

    @validates('imei')
    def _validate_imei(self, value):
        """Validator to validate imei field."""
        if len(value) < GLOBAL_CONF.get('min_imei_length'):
            raise ValidationError("IMEI is invalid", fields=['imei'])
        if len(value) > GLOBAL_CONF.get('max_imei_length'):
            raise ValidationError("IMEI is invalid", fields=['imei'])

    @validates('uid')
    def _validate_uid(self, value):
        """Validator to validate uid field."""
        if len(value) == 0:
            raise ValidationError("UID is invalid", fields=['uid'])
        match = re.match(r'^[a-zA-Z0-9\x2d]{10,20}$', value)
        if match is None:
            raise ValidationError("UID format is invalid", fields=['uid'])
