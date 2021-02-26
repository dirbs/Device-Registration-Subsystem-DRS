"""
DRS Seeds package.
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
import logging

from flask_script import Command  # pylint: disable=deprecated-module
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.models import technologies, documents, status, devicetype
from app import ConfigParser, app


class Seed(Command):
    """Class to define seed command for database seeding."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.logger = self.__create_logger()

    def __create_logger(self):
        """Method t create a custom logger with console handler."""
        logger = logging.getLogger('db_operations')
        logger.setLevel(logging.INFO)

        # create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # set formatter
        formatter = logging.Formatter('>> %(name)s: %(message)s')
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        return logger

    def seed_technologies(self):
        """Method to seed supported technologies to the database."""
        try:
            objects = [technologies.Technologies(id=1, description='2G'),
                       technologies.Technologies(id=2, description='3G'),
                       technologies.Technologies(id=3, description='4G'),
                       technologies.Technologies(id=4, description='5G')]

            sql = "select count(*) from technologies"
            data = self.db.engine.execute(sql).fetchone()
            if data[0] > 0:
                self.db.engine.execute("TRUNCATE table technologies RESTART IDENTITY CASCADE")
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Technologies seeding successful."
            else:
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Technologies seeding successful."
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e

    def seed_documents(self):
        """Method to seed supported documents to the database."""
        # read and load DRS base configuration to the app
        try:
            config = ConfigParser('etc/config.yml').parse_config()
        except Exception as e:
            app.logger.critical('exception encountered while parsing the config file, see details below')
            app.logger.exception(e)
            sys.exit(1)
        try:
            automate_imei_check = False if config['automate_imei_check'] else True
            objects = [
                documents.Documents(id=1, label='shipment document', type=1, required=automate_imei_check ),
                documents.Documents(id=2, label='authorization document', type=1, required=automate_imei_check),
                documents.Documents(id=3, label='certificate document', type=1, required=automate_imei_check),
                documents.Documents(id=4, label='shipment document', type=2, required=automate_imei_check),
                documents.Documents(id=5, label='authorization document', type=2, required=automate_imei_check),
                documents.Documents(id=6, label='certificate document', type=2, required=automate_imei_check)
            ]

            sql = "select count(*) from documents"
            data = self.db.engine.execute(sql).fetchone()
            if data[0] > 0:
                self.db.engine.execute("TRUNCATE table documents RESTART IDENTITY CASCADE")
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Documents seeding successful."
            else:
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Documents seeding successful."
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e

    def seed_device_types(self):
        """Method to seed supported device types to the database."""
        try:
            objects = [devicetype.DeviceType(id=1, description='Smartphone'),
                       devicetype.DeviceType(id=2, description='Tablet'),
                       devicetype.DeviceType(id=3, description='Feature phone'),
                       devicetype.DeviceType(id=4, description='Computer'),
                       devicetype.DeviceType(id=5, description='Dongle'),
                       devicetype.DeviceType(id=6, description='Router'),
                       devicetype.DeviceType(id=7, description='Vehicle'),
                       devicetype.DeviceType(id=8, description='Other')]

            sql = "select count(*) from devicetype"
            data = self.db.engine.execute(sql).fetchone()
            if data[0] > 0:
                self.db.engine.execute("TRUNCATE table devicetype RESTART IDENTITY CASCADE")
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Device Types seeding successful."
            else:
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Device Types seeding successful."
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e

    def seed_status(self):
        """Method to seed supported statuses to the database."""
        try:
            objects = [status.Status(id=1, description='New Request'),
                       status.Status(id=2, description='Awaiting Documents'),
                       status.Status(id=3, description='Pending Review'),
                       status.Status(id=4, description='In Review'),
                       status.Status(id=5, description='Information Requested'),
                       status.Status(id=6, description='Approved'),
                       status.Status(id=7, description='Rejected'),
                       status.Status(id=8, description='Closed'),
                       status.Status(id=9, description='Failed'),
                       status.Status(id=10, description='Processed'),
                       status.Status(id=11, description='Processing')]

            sql = "select count(*) from status"
            data = self.db.engine.execute(sql).fetchone()
            if data[0] > 0:
                self.db.engine.execute("TRUNCATE table status RESTART IDENTITY CASCADE")
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Status seeding successful."
            else:
                self.db.session.bulk_save_objects(objects)
                self.db.session.commit()
                return "Status seeding successful."
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise e

    def __seed_database(self):
        """Method to perform pre-functional database seeding."""
        seeder = Seed(self.db)
        try:
            self.logger.info(seeder.seed_technologies())
            self.logger.info(seeder.seed_device_types())
            self.logger.info(seeder.seed_status())
            self.logger.info(seeder.seed_documents())
        except SQLAlchemyError as e:
            self.logger.error('an unknown error occured during seeding, see the logs below for details')
            self.logger.exception(e)
            sys.exit(1)

    def run(self):  # pylint: disable=method-hidden
        """Overridden method."""
        self.logger.info('seeding data into the database')
        self.__seed_database()
