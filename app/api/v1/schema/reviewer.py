"""
DRS reviewer package.
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
from enum import Enum
from marshmallow import Schema, fields, validates, ValidationError, post_dump, validate, pre_dump


class RequestTypes(Enum):
    """Enum for supported request types for comments api."""

    REG_REQUEST = 'registration_request'
    DEREG_REQUEST = 'de_registration_request'


class UpdateReviewerArgs(Schema):
    """Schema for Update Request Reviewer."""

    request_id = fields.Integer(required=True,
                                description='Tracking Id of the Request',
                                error_messages={'required': 'request id is required'},
                                missing=None)
    reviewer_id = fields.String(required=True,
                                description='Reviewer Id to assign request to',
                                error_messages={'required': 'reviewer id is required'},
                                missing=None)
    reviewer_name = fields.String(required=True,
                                  description='Name of the reviewer',
                                  missing=None)
    request_type = fields.String(required=True,
                                 description='Request Type',
                                 validate=validate.OneOf([f.value for f in RequestTypes]),
                                 missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields

    @validates('request_id')
    def _validate_request_id(self, value):
        """Validator to validate request_id field."""
        try:
            int(value)
        except Exception:
            raise ValidationError('Request Id must be an integer', fields=['request_id'])

    @validates('reviewer_id')
    def _validate_reviewer_id(self, value):
        """Validator to validate reviewer_id field."""
        if not type(value) is str:
            raise ValidationError('reviewer_id must be a valid string', fields=['reviewer_id'])


class UnAssignReviewerArgs(Schema):
    """Args for un-assign reviewer route"""

    request_id = fields.Integer(required=True,
                                description='Tracking Id of the Request',
                                error_messages={'required': 'request id is required'},
                                missing=None)
    reviewer_id = fields.String(required=True,
                                description='Reviewer Id to assign request to',
                                error_messages={'required': 'reviewer id is required'},
                                missing=None)

    request_type = fields.String(required=True,
                                 description='Request Type',
                                 validate=validate.OneOf([f.value for f in RequestTypes]),
                                 missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class SuccessResponse(Schema):
    """Response schema for successful response."""

    message = fields.String(required=True)


class SubmitSuccessResponse(Schema):
    """Response schema for submit-review process."""

    request_id = fields.Integer(required=True)
    request_type = fields.String(required=True)
    status = fields.Integer(required=True)
    message = fields.String(required=True)


class ErrorResponse(Schema):
    """Response schema for response in case of error."""

    error = fields.List(fields.String(required=True), required=True)


class DeviceQuota(Schema):
    """Response schema for Device Quota api."""

    SKIP_VALUES = set([None])

    allowed_import_quota = fields.Integer(required=True)
    allowed_export_quota = fields.Integer(required=True)
    used_registration_quota = fields.Integer(required=False)
    used_de_registration_quota = fields.Integer(required=False)
    request_device_count = fields.Integer(required=True)

    @post_dump
    def skip_null_fields(self, data):
        """Method to skip null value fields."""
        return {
            key: value for key, value in data.items()
            if value not in self.SKIP_VALUES
        }


class DeviceQuotaArgs(Schema):
    """Args schema for Device Quota Api."""

    request_id = fields.Integer(required=True,
                                description='Tracking Id of the Request',
                                error_messages={'required': 'request id is required'},
                                missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields

    @validates('request_id')
    def _validate_request_id(self, value):
        """Validator to validate request_id field."""
        try:
            int(value)
        except Exception:
            raise ValidationError('Request Id must be an integer', fields=['request_id'])

    @validates('user_id')
    def _validate_reviewer_id(self, value):
        """Validator to validate reviewer_id field."""
        if not type(value) is str:
            raise ValidationError('reviewer_id must be a valid string', fields=['reviewer_id'])


class SectionTypes(Enum):
    """Enum for supported section types."""

    DEVICE_QUOTA = 'device_quota'
    DEVICE_DESCP = 'device_description'
    IMEI_CLASSIFICATION = 'imei_classification'
    IMEI_REGISTRATION = 'imei_registration'
    APPROVAL_DOCS = 'approval_documents'


class StatusTypes(Enum):
    """Enum for supported status types for section approval."""

    APPROVED = 6
    REJECTED = 7
    INFORMATION_REQUESTED = 5


class SectionComment(Schema):
    """Schema for section comments."""

    user_id = fields.String(required=True)
    user_name = fields.String(required=True)
    comment = fields.String(required=True, missing='')
    datetime = fields.DateTime(required=True)


class SectionReviewArgs(Schema):
    """Args schema for Section review api."""

    section = fields.String(required=True,
                            description='Approval section types',
                            validate=validate.OneOf([f.value for f in SectionTypes]),
                            missing=None)
    request_type = fields.String(required=True,
                                 description='Request Type',
                                 validate=validate.OneOf([f.value for f in RequestTypes]),
                                 missing=None)
    reviewer_id = fields.String(required=True,
                                description='Id of the reviewer',
                                missing=None)
    reviewer_name = fields.String(required=True,
                                  description='Name of the reviewer',
                                  missing=None)
    comment = fields.String(required=True,
                            missing='')
    request_id = fields.Integer(required=True,
                                description='Id of the current request',
                                missing=None)
    status = fields.Integer(required=True,
                            description='Status of the current section',
                            missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class DeviceDescription(Schema):
    """Schema for a single device description."""

    brand = fields.String(required=False)
    model_name = fields.String(required=False)
    model_number = fields.String(required=False)
    device_type = fields.String(required=False)
    operating_system = fields.String(required=True)
    radio_access_technology = fields.String(required=False)

    @pre_dump
    def assign_proper_keys(self, data):
        """Method to assign proper keys into data before dumping."""
        if data.get('brand_name') is not None:
            data['brand'] = data.pop('brand_name')
        if data.get('internal_model_name') is not None:
            data['model_number'] = data.pop('internal_model_name')
        if data.get('device_type') is not None:
            data['device_type'] = data.pop('device_type')
        if data.get('gsma_device_type') is not None:
            data['device_type'] = data.pop('gsma_device_type')
        if data.get('radio_interface') is not None:
            data['radio_access_technology'] = data.pop('radio_interface')
        if data.get('operating_system') is None:
            data['operating_system'] = 'N/A'


class DevicesDescription(Schema):
    """Response Schema for Devices Description API."""

    user_device_description = fields.List(fields.Nested(DeviceDescription, required=True))
    gsma_device_description = fields.List(fields.Nested(DeviceDescription, required=True))


class DeviceDescriptionArgs(Schema):
    """Args schema for Devices Description Route."""

    request_type = fields.String(required=True,
                                 description='Type of the current request',
                                 validate=validate.OneOf([f.value for f in RequestTypes]))
    request_id = fields.Integer(required=True, description='Id of the current request')

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class IMEIRegStatus(Schema):
    """Response Schema for IMEI Registration status."""

    pending_registration = fields.Integer(required=True)
    registered = fields.Integer(required=True)
    not_registered = fields.Integer(required=True)
    duplicated = fields.Integer(required=True)
    invalid = fields.Integer(required=True)


class IMEIRegStatusArgs(Schema):
    """Args schema for IMEI Registration status."""

    request_id = fields.Integer(required=True,
                                description='Current request id',
                                missing=None)
    request_type = fields.String(required=True,
                                 description='Current request type',
                                 validate=validate.OneOf([f.value for f in RequestTypes]),
                                 missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class Document(Schema):
    """Response schema for a document of document api."""

    document_type = fields.String(required=True)
    link = fields.String(required=True)


class Documents(Schema):
    """Response schema for document api."""

    documents = fields.List(fields.Nested(Document, required=True))


class DocumentsApiArgs(Schema):
    """Args schema for documents API."""

    request_type = fields.String(required=True,
                                 description='Current request type',
                                 validate=validate.OneOf([f.value for f in RequestTypes]),
                                 missing=None)
    request_id = fields.Integer(required=True, description='current request id', missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class SectionsArgs(Schema):
    """Args schema for sections route."""

    request_type = fields.String(required=True,
                                 description='Current request type',
                                 validate=validate.OneOf([f.value for f in RequestTypes]),
                                 missing=None)
    request_id = fields.Integer(required=True, description='Current request id', missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class SubmitReviewArgs(Schema):
    """Args schema for submit-review route."""

    request_type = fields.String(required=True,
                                 description='Current request type',
                                 validate=validate.OneOf([f.value for f in RequestTypes]),
                                 missing=None)
    request_id = fields.Integer(required=True, description='Current request id', missing=None)
    reviewer_id = fields.String(required=True, description='Id of the reviewer', missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class Section(Schema):
    """Response schema for each section in sections schema."""

    section_type = fields.String(required=True)
    section_status = fields.Integer(required=True)
    comments = fields.List(fields.Nested(SectionComment, required=True))


class Sections(Schema):
    """Response schema for sections route."""

    sections = fields.List(fields.Nested(Section, required=True))


class IMEIComplianceCount(Schema):
    """Schema for IMEI Complience count."""

    compliant_imeis = fields.Integer(required=True)
    non_compliant_imeis = fields.Integer(required=True)
    provisional_compliant = fields.Integer(required=True)
    provisional_non_compliant = fields.Integer(required=True)


class IMEILostStolenCount(Schema):
    """Schema for IMEI Lost Stolen Count."""

    provisional_stolen = fields.Integer(required=True)
    stolen = fields.Integer(required=True)


class IMEIClassification(Schema):
    """Response schema for IMEI classification route."""
    imei_compliance_status = fields.Nested(IMEIComplianceCount, required=True)
    per_condition_classification_state = fields.Dict(required=True)
    lost_stolen_status = fields.Nested(IMEILostStolenCount, required=True)
    seen_on_network = fields.Integer(required=True)
    associated_imeis = fields.Integer()
