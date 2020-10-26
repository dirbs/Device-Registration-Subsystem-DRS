"""
DRS Indexer package.
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
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.models.approvedimeis import ApprovedImeis
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.regdevice import RegDevice
from app.api.v1.models.deregdetails import DeRegDetails
from app.api.v1.models.deregdevice import DeRegDevice
from app.api.v1.models.deregimei import DeRegImei
from app.api.v1.models.imeidevice import ImeiDevice
from app.api.v1.models.device import Device


class Indexer:
    """Class for indexing the database tables and views."""

    def __init__(self, db):
        """Constructor."""
        self.db = db

    def index_approved_imeis(self, conn):
        """Method to index the approved_imeis table."""

        try:
            ApprovedImeis.create_index(conn)
            return "Approved imeis indexed successfully"
        except SQLAlchemyError as e:
            raise e

    def index_dereg_comments(self):
        """ skeleton method for
            De-Registration comments"""

        pass

    def index_dereg_details(self, conn):
        """Method to index the De-Registration Details table."""

        try:
            DeRegDetails.create_index(conn)
            return "De-Registration Detail indexed successfully"
        except SQLAlchemyError as e:
            raise e

    def index_dereg_device(self, conn):
        """Method to index the De-Registration Device table."""

        try:
            DeRegDevice.create_index(conn)
            return "De-Registration Device indexed successfully"
        except SQLAlchemyError as e:
            raise e

    def index_dereg_documents(self):
        """ Skeleton method for indexing
            De-Registration Documents table"""

        pass

    def index_de_regimei(self, conn):
        """Method to index the De-Registration imei table."""

        try:
            DeRegImei.create_index(conn)
            return "De-Registration Imei indexed successfully"
        except SQLAlchemyError as e:
            raise e

    def index_device(self, conn):
        """Method to index the Registration Device table."""

        try:
            Device.create_index(conn)
            return "Registration Device indexed successfully"
        except SQLAlchemyError as e:
            raise e

    def index_device_quota(self):
        """ Skeleton method for indexing
            device quota table"""

        pass

    def index_device_technology(self):
        """ Skeleton method for indexing
            device technology table"""

        pass

    def index_imei_device(self, conn):
        """Method to index the Registration Device table."""

        try:
            ImeiDevice.create_index(conn)
            return "Registration Imeidevice indexed successfully"
        except SQLAlchemyError as e:
            raise e

    def index_notification(self):
        """ Skeleton method for indexing
            notification table"""

        pass

    def index_reg_comments(self):
        """ Skeleton method for indexing
            Reg-Comments table"""

        pass

    def index_reg_details(self, conn):
        """Method to index the Registration Details."""

        try:
            RegDetails.create_index(conn)
            return "Registration Details indexed successfully"
        except SQLAlchemyError as e:
            raise e

    def index_reg_device(self, conn):
        """Method to index the Registration Device."""

        try:
            RegDevice.create_index(conn)
            return "Registration Device indexed successfully"
        except SQLAlchemyError as e:
            raise e

    def index_reg_documents(self):
        """ Skeleton method for indexing
            Reg-Documents table"""

        pass
