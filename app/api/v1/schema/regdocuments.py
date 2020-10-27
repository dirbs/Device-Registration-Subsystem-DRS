"""
DRS Registration document schema package.
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
from app.api.v1.models.documents import Documents
from marshmallow import Schema, fields, validates, ValidationError, pre_load, pre_dump
from app.api.v1.helpers.validators import *
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.documents import Documents
from app.api.v1.helpers.error_handlers import ALLOWED_FORMATS
from app.api.v1.models.status import Status
from app import app, GLOBAL_CONF
from flask_babel import lazy_gettext as _


class RegistrationDocumentsSchema(Schema):
    """Schema for Regisration Documents routes."""

    id = fields.Int()
    filename = fields.Str()
    document_id = fields.Int()
    label = fields.Str()
    required = fields.Boolean()
    link = fields.Str()
    reg_details_id = fields.Int(required=True, error_messages={'required': 'reg_details_id is required'})
    user_id = fields.Str(required=True, error_messages={'required': 'user_id is required'})

    @pre_dump()
    def get_document_label(self, data):
        """Returns appropriate document label"""
        reg_details = RegDetails.get_by_id(data.reg_details_id)
        upload_dir_path = GLOBAL_CONF['upload_directory']
        document = Documents.get_document_by_id(data.document_id)
        data.label = document.label
        data.required = Documents.required
        data.link = '{server_dir}/{local_dir}/{file_name}'.format(
                                server_dir=upload_dir_path,
                                local_dir=reg_details.tracking_id,
                                file_name=data.filename
                            )

    @pre_load()
    def validate_format(self, data):
        """Validates document format."""
        for filename in data['files'].keys():
            filename = data['files'][filename]
            doc_format = filename.rsplit('.', 1)[1]
            if doc_format not in ALLOWED_FORMATS:
                raise ValidationError(_('File format %(format)s is not allowed', format=doc_format),
                                      field_names=['document_format'])

    @pre_load()
    def validate_file_name(self, data):
        """Validates file name."""
        filenames = []
        for filename in data['files'].keys():
            if data['files'].get(filename) not in filenames:
                filenames.append(data['files'].get(filename))
            else:
                raise ValidationError(_('File names should be unique'),
                                      field_names=['filename'])

    @pre_load()
    def validate_filecount(self, data):
        """Validates total files count."""
        if not data or data['files'].keys() is None:
            raise ValidationError('No file is provided', field_names=['id'])

    @pre_load()
    def validate_required_docs(self, data):
        """Validates required documents."""
        required = Documents.get_required_docs('registration')
        labels = list(map(lambda document: document.label, required))
        missing_required = list(filter(lambda x: x not in data['files'], labels))
        if len(missing_required) > 0:
            raise ValidationError('This is a required Document', field_names=missing_required)

    @pre_load()
    def check_reg_id(self, data):
        """Validates request id."""
        reg_details_id = data['reg_details_id']
        reg_details = RegDetails.get_by_id(reg_details_id)
        if not reg_details:
            raise ValidationError('The request id provided is invalid', field_names=['reg_id'])
        if 'user_id' in data and reg_details.user_id != data['user_id']:
            raise ValidationError('Permission denied for this request', field_names=['user_id'])
        else:
            status = Status.get_status_type(reg_details.status)
            if status != 'Awaiting Documents':
                raise ValidationError(_('This step can only be performed for request with Awaiting Document status'),
                                      field_names=['status'])


