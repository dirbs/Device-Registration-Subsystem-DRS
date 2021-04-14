"""
DRS Database Script Module

Copyright (c) 2018-2021 Qualcomm Technologies, Inc.
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
import sys

from flask_script import Command  # pylint: disable=deprecated-module
from sqlalchemy.exc import SQLAlchemyError

from scripts.common import ScriptLogger
from scripts.db.indexer import Indexer
from scripts.db.views import Views
from scripts.db.seeders import Seed


class CreateDatabase(Command):
    """Class to manage database post creation operations."""

    def __init__(self, db):
        """Constructor"""
        super().__init__()
        self.db = db
        self.logger = ScriptLogger('db_operations').get_logger()

    def _create_views(self):
        """Method to auto create views and materialized views on database."""
        db_views = Views(self.db)
        try:
            self.logger.info(db_views.create_registration_view())
            self.logger.info(db_views.create_de_registration_view())
        except SQLAlchemyError as e:
            self.logger.error('an unknown error occured during creating views, see the logs below for details')
            self.logger.exception(e)
            sys.exit(1)

    def __create_indexes(self):
        """Method to perform database indexing."""
        db_indexer = Indexer(self.db)

        with self.db.engine.connect() as conn:
            with conn.execution_options(isolation_level='AUTOCOMMIT'):
                try:
                    self.logger.info(db_indexer.index_approved_imeis(conn))
                    self.logger.info(db_indexer.index_de_regimei(conn))
                    self.logger.info(db_indexer.index_dereg_details(conn))
                    self.logger.info(db_indexer.index_dereg_device(conn))
                    self.logger.info(db_indexer.index_device(conn))
                    self.logger.info(db_indexer.index_imei_device(conn))
                    self.logger.info(db_indexer.index_reg_device(conn))
                    self.logger.info(db_indexer.index_reg_details(conn))

                except SQLAlchemyError as e:
                    self.logger.error('an unknown error occured during indexing, see the logs below for details')
                    self.logger.exception(e)
                    sys.exit(1)

    # method id overridden so disable pylint warning
    def run(self):  # pylint: disable=method-hidden
        """Overridden method."""
        self.logger.info('creating views/materialized views on database')
        self._create_views()

        self.logger.info('creating indexes on database tables/views')
        self.__create_indexes()
