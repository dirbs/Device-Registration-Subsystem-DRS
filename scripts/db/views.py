"""
DRS Views package.
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

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


class Views:
    """Class for creating/migrating views into the database."""

    def __init__(self, db):
        """Constructor."""
        self.db = db

    def create_registration_view(self):
        """Method to create registration view for search function."""
        query = text("""CREATE OR REPLACE VIEW public.search_registration
                            AS SELECT regdetails.id,
                                      regdetails.tracking_id, 
                                      regdetails.created_at, 
                                      regdetails.updated_at, 
                                      regdetails.user_name, 
                                      regdetails.device_count::character varying AS device_count, 
                                      regdetails.imei_per_device::character varying AS imei_per_device, 
                                      regdetails.m_location,
                                      regdetails.processing_status,
                                      regdetails.report_status, 
                                      status.description AS status,
                                      regdevice.brand,
                                      regdevice.model_name,
                                      regdevice.operating_system,
                                      devicetype.description AS device_type,
                                      string_agg(DISTINCT imeidevice.imei::text, ', '::text) AS imeis,
                                      1::smallint AS request_type,
                                      regdetails.reviewer_id,
                                      regdetails.reviewer_name,
                                      regdetails.user_id,
                                      regdetails.report,
                                      regdevice.model_num,
                                      string_agg(DISTINCT technologies.description::text, ', '::text) AS technologies 
                                 FROM regdetails 
                                JOIN status ON status.id = regdetails.status 
                                LEFT JOIN device ON device.reg_details_id = regdetails.id 
                                LEFT JOIN regdevice ON regdevice.id = device.reg_device_id 
                                LEFT JOIN devicetechnology ON devicetechnology.reg_device_id = regdevice.id 
                                LEFT JOIN technologies ON technologies.id = devicetechnology.technology_id 
                                LEFT JOIN devicetype ON devicetype.id = regdevice.device_types_id 
                                LEFT JOIN imeidevice ON imeidevice.device_id = device.id 
                            GROUP BY regdetails.id, 
                                     status.description, 
                                     regdetails.tracking_id, 
                                     regdetails.updated_at, 
                                     regdetails.user_name, 
                                     regdetails.device_count, 
                                     regdetails.imei_per_device, 
                                     regdetails.m_location, 
                                     regdevice.brand, 
                                     regdevice.model_name, 
                                     regdevice.operating_system, 
                                     devicetype.description,
                                     regdetails.report,
                                     regdevice.model_num;""")

        try:
            self.db.engine.execute(query)
            return 'registration view created successfully'
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e

    def create_de_registration_view(self):
        """Method to create de-registration view for search function."""
        query = text("""CREATE OR REPLACE VIEW public.search_deregistration
                            AS SELECT deregdetails.id,
                                      deregdetails.tracking_id,
                                      deregdetails.created_at,
                                      deregdetails.updated_at,
                                      deregdetails.user_name,
                                      deregdetails.device_count::character varying,
                                      deregdetails.processing_status,
                                      deregdetails.report_status,
                                      status.description AS status,
                                      deregdevice.brand,
                                      deregdevice.model_name,
                                      deregdevice.operating_system,
                                      deregdevice.device_type,
                                      string_agg(DISTINCT deregimei.imei::text, ', '::text) AS imeis,
                                      2::smallint AS request_type,
                                      deregdetails.reviewer_id,
                                      deregdetails.reviewer_name,
                                      deregdetails.user_id,
                                      deregdetails.report,
                                      deregdevice.model_num,
                                      deregdevice.technology AS technologies 
                                 FROM deregdetails 
                                JOIN status ON status.id = deregdetails.status 
                                LEFT JOIN deregdevice ON deregdevice.dereg_details_id = deregdetails.id 
                                LEFT JOIN deregimei ON deregimei.device_id = deregdevice.id 
                            GROUP BY deregdetails.id, 
                                     status.description, 
                                     deregdetails.tracking_id, 
                                     deregdetails.updated_at, 
                                     deregdetails.user_name, 
                                     deregdetails.device_count, 
                                     deregdevice.brand, 
                                     deregdevice.model_name, 
                                     deregdevice.operating_system, 
                                     deregdevice.device_type,
                                     deregdetails.report,
                                     deregdevice.model_num,
                                     deregdevice.technology;""")
        try:
            self.db.engine.execute(query)
            return 'de-registration view created successfully'
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e
