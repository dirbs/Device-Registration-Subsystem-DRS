"""
DRS Common schema package.
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
from marshmallow import Schema, fields, validate


class UserTypes(Enum):
    """Enum for supported user types."""

    EXPORTER = 'exporter'
    IMPORTER = 'importer'
    REVIEWER = 'reviewer'
    INDIVIDUAL = 'individual'


class RequestTypes(Enum):
    """Enum for supported request types for comments api."""

    REG_REQUEST = 'registration_request'
    DEREG_REQUEST = 'de_registration_request'


class FileArgs(Schema):
    """Args schema for file downloading route."""

    path = fields.String(required=True, missing='')

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class Common(Schema):
    """Response schema for supported technologies, devices & statuses."""

    id = fields.Integer(required=True, description='ID of the type')
    description = fields.String(required=True, description='Description of the type')


class Document(Schema):
    """Response Schema for supported document types."""

    id = fields.Integer(required=True, description='ID of the document')
    label = fields.String(required=True, description='Label of the document')
    type = fields.Integer(required=True, description='Type of the document')
    required = fields.Boolean(required=True, description='Weather the document is required or not')


class SysConfing(Schema):
    label = fields.String(required=False, description='Label of the configuration')
    flag = fields.Boolean(required=False, description='True or False')


class Documents(Schema):
    """Response schema for supported documents."""

    registration = fields.List(fields.Nested(Document, required=True),
                               required=False,
                               description='List of supported documents for registration')
    de_registration = fields.List(fields.Nested(Document, required=True),
                                  required=False,
                                  description='List of supported documents for de-registration')


class ServerConfigs(Schema):
    """Response schema for server-config route."""

    technologies = fields.List(fields.Nested(Common, required=True),
                               required=False,
                               description='List of the supported technologies')
    documents = fields.Nested(Documents, required=False, description='Supported document types')
    status_types = fields.List(fields.Nested(Common, required=True),
                               required=False,
                               description='List of the supported status types')
    device_types = fields.List(fields.Nested(Common, required=True),
                               required=False,
                               description='List of the supported device types')
    system_config = fields.List(fields.Nested(SysConfing, required=True),
                               required=False,
                               description='List of configured features')


class RequestStatusTypes(Enum):
    """Schema for status types of a request when in the review process."""

    approved = 6
    rejected = 7
    closed = 8


class ErrorResponse(Schema):
    """Response schema for response in case of error."""

    error = fields.List(fields.String(required=True), required=True)


class SuccessResponse(Schema):
    """Response schema for successful response."""

    message = fields.String(required=True)


class DashboardReportsArgs(Schema):
    """Schema for Dashboard reports request."""

    user_id = fields.String(required=True,
                            description='User Id to fetch statistics from database',
                            error_messages={'required': 'user id is required'},
                            validate=validate.Length(min=1),
                            missing=None)
    user_type = fields.String(required=True,
                              description='User Type to fetch statistics from database',
                              error_messages={'required': 'user type is required'},
                              validate=validate.OneOf([f.value for f in UserTypes]),
                              missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class ImieReportsArgsGet(Schema):
    """Schema for Imei reports request"""

    user_id = fields.String(required=True,
                            description='User Id to fetch statistics from database',
                            error_messages={'required': 'user id is required'},
                            validate=validate.Length(min=1),
                            missing=None)

    request_type = fields.String(required=True,
                                 description='Request Type to fetch report',
                                 error_messages={'required': 'request type is required'},
                                 validate=validate.OneOf([f.value for f in RequestTypes]),
                                 missing=None)

    request_id = fields.String(required=True,
                               description='Request Id to get the report of database',
                               error_messages={'required': 'request id is required'},
                               validate=validate.Length(min=1),
                               missing=None)

    user_type = fields.String(required=True,
                              description='User Type to fetch statistics from database',
                              error_messages={'required': 'user type is required'},
                              validate=validate.OneOf(['reviewer', 'exporter', 'importer', 'individual']),
                              missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class ImieReportsArgsPost(ImieReportsArgsGet):
    """Schema for Imei reports request"""

    user_id = fields.String(required=True,
                            description='User Id to fetch statistics from database',
                            error_messages={'required': 'user id is required'},
                            validate=validate.Length(min=1),
                            missing=None)

    request_type = fields.String(required=True,
                                 description='Request Type to fetch report',
                                 error_messages={'required': 'request type is required'},
                                 validate=validate.OneOf([f.value for f in RequestTypes]),
                                 missing=None)

    request_id = fields.String(required=True,
                               description='Request Id to get the report of database',
                               error_messages={'required': 'request id is required'},
                               validate=validate.Length(min=1),
                               missing=None)

    user_type = fields.String(required=True,
                              description='User Type to fetch statistics from database',
                              error_messages={'required': 'user type is required'},
                              validate=validate.OneOf(['reviewer']),
                              missing=None)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields
