"""
DRS route package.
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
from flask_restful import Api

from app import app

from app.api.v1.resources.search import Search
from app.api.v1.helpers.error_handlers import CustomErrors
from app.api.v1.resources.notification import Notification
from app.api.v1.resources.regdetails import RegistrationRoutes
from app.api.v1.resources.deregdevice import DeRegDeviceRoutes
from app.api.v1.resources.regdocuments import RegDocumentRoutes
from app.api.v1.resources.deregdetails import DeRegistrationRoutes
from app.api.v1.resources.deregdocuments import DeRegDocumentRoutes
from app.api.v1.resources.regdevicedetails import DeviceDetailsRoutes
from app.api.v1.resources.common import BaseRoutes, ServerConfigs, Files
from app.api.v1.resources.version import Version
from app.api.v1.resources.health import HealthCheck
from app.api.v1.resources.reviewer import AssignReviewer, ReviewSection, DeviceQuota, DeviceDescription, \
  IMEIRegistrationStatus, RequestDocuments, Sections, SubmitReview, IMEIClassification, UnAssignReviewer
from app.common.apidoc import ApiDocs
from app.api.v1.resources.reports import ImeiReport, GetDashBoardReports, SetImeiReportPermissions
from app.api.v1.resources.regdetails import RegSectionRoutes
from app.api.v1.resources.deregdetails import DeRegSectionRoutes
from app.api.v1.resources.restart_process import RegistrationProcessRestart, DeRegistrationProcessRestart
from .resources.deassociate import DeassociateImeis
from .resources.associate import AssociateImeis, AssociateDuplicate
from app.api.v1.resources.ussd import Register_ussd
from app.api.v1.resources.ussd import Track_record_ussd
from app.api.v1.resources.ussd import Delete_record_ussd
from app.api.v1.resources.ussd import Ussd_records_count
from app.api.v1.resources.ussd_scripts import Send, SendBatchTest
from app.api.v1.resources.ussd_scripts import Ussd_Script

api = Api(app, prefix='/api/v1', errors=CustomErrors)
apidoc = ApiDocs(app, 'v1')

# registration routes
api.add_resource(BaseRoutes, '/sample/<request_type>')
api.add_resource(RegistrationRoutes, '/registration', '/registration/<reg_id>')
api.add_resource(DeviceDetailsRoutes, '/registration/device/<reg_id>', '/registration/device')
api.add_resource(RegDocumentRoutes, '/registration/documents/<reg_id>', '/registration/documents')
api.add_resource(RegSectionRoutes, '/registration/sections/<reg_id>')
# api.add_resource(, '/registration/restart/<reg_id>')

# de-registration routes
api.add_resource(DeRegistrationRoutes, '/deregistration', '/deregistration/<dereg_id>')
api.add_resource(DeRegDeviceRoutes, '/deregistration/devices/<dereg_id>', '/deregistration/devices')
api.add_resource(DeRegDocumentRoutes, '/deregistration/documents/<dereg_id>', '/deregistration/documents')
api.add_resource(DeRegSectionRoutes, '/deregistration/sections/<dereg_id>')

# common routes
# api.add_resource(RestartProcess, '/deregistration/restart/<request_id>', '/registration/restart/<request_id>')

# reviewer routes
api.add_resource(AssignReviewer, '/review/assign-reviewer')
api.add_resource(UnAssignReviewer, '/review/unassign-reviewer')
api.add_resource(ReviewSection, '/review/review-section')
api.add_resource(DeviceQuota, '/review/device-quota')
api.add_resource(DeviceDescription, '/review/device-description')
api.add_resource(IMEIRegistrationStatus, '/review/imeis-status')
api.add_resource(RequestDocuments, '/review/documents')
api.add_resource(Sections, '/review/sections')
api.add_resource(SubmitReview, '/review/submit-review')
api.add_resource(IMEIClassification, '/review/imei-classification')

# restart process if failed
api.add_resource(RegistrationProcessRestart, '/review/restart/registration/<reg_id>')
api.add_resource(DeRegistrationProcessRestart, '/review/restart/deregistration/<dereg_id>')

# files
api.add_resource(Files, '/files/download')

# server configs
api.add_resource(ServerConfigs, '/config/server-config')

# notifications
api.add_resource(Notification, '/notification')

# search
api.add_resource(Search, '/search')

# dashboard reports
api.add_resource(GetDashBoardReports, '/dashboard/report')

# imei-reports
api.add_resource(ImeiReport, '/report/download')
api.add_resource(SetImeiReportPermissions, '/report/permission')


# healthcheck
api.add_resource(HealthCheck, '/healthcheck')

# version
api.add_resource(Version, '/version')

api.add_resource(DeassociateImeis, '/deassociate')

api.add_resource(AssociateImeis, '/associate', '/associate/<uid>')

api.add_resource(AssociateDuplicate, '/associate_duplicate')


# USSD registrations
api.add_resource(Register_ussd, '/register_ussd')

# Track records using USSD
api.add_resource(Track_record_ussd, '/track_record_ussd')

# Deleting record using USSD
api.add_resource(Delete_record_ussd, '/delete_record_ussd')

# Count registered applications USSD
api.add_resource(Ussd_records_count, '/ussd_records_count')

# test controller for testing purposes
api.add_resource(Send, '/send')
api.add_resource(SendBatchTest, '/sendbatch')
api.add_resource(Ussd_Script, '/ussd_script')


docs = apidoc.init_doc()


def register_docs():
    """Method to register routes for docs."""
    for route in [AssignReviewer, DeviceQuota, ReviewSection, DeviceDescription, IMEIRegistrationStatus,
                  RequestDocuments, Files, Sections, SubmitReview, IMEIClassification, UnAssignReviewer,
                  ServerConfigs, Notification, HealthCheck, Version, DeassociateImeis, AssociateImeis,
                  AssociateDuplicate]:
        docs.register(route)
