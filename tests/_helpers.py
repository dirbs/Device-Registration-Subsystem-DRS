"""
DRS Unit Test helper module.
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
import os
import uuid
import datetime

from sqlalchemy import text

from scripts.db.seeders import Seed
from scripts.db.views import Views
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.deregdetails import DeRegDetails
from app.api.v1.models.regdevice import RegDevice
from app.api.v1.models.devicetechnology import DeviceTechnology
from app.api.v1.models.device import Device
from app.api.v1.models.deregdevice import DeRegDevice
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.models.deregimei import DeRegImei
from app.api.v1.models.regdocuments import RegDocuments
from app.api.v1.models.deregdocuments import DeRegDocuments
from app.api.v1.models.documents import Documents


def seed_database(db):
    """Helper method to seed data into the database."""
    seeder = Seed(db)
    seeder.seed_technologies()
    seeder.seed_status()
    seeder.seed_device_types()
    seeder.seed_documents()


def create_views(db):
    """Helper method to index database and create views."""
    db_views = Views(db)
    db_views.create_registration_view()
    db_views.create_de_registration_view()


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
def get_notification_id(session, request_id):
    """Helper Method to extract a notification's id from notification
    table using raw SQL rather than using the sqlalchmey model.
    """
    res = session.execute(text("""SELECT id
                                        FROM public.notification
                                       WHERE request_id='{0}'""".format(request_id))).fetchone()
    return res.id


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
def get_single_notification(session, notification_id):
    """Helper method to extract a single notification from notification table."""
    return session.execute(text("""SELECT *
                                    FROM public.notification
                                   WHERE id='{0}'""".format(notification_id))).fetchone()


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
def get_user_notifications(session, user_id):
    """Helper method to extract a user's notifications from table."""
    return session.execute(text("""SELECT *
                                              FROM public.notification
                                             WHERE user_id='{0}'""".format(user_id))).fetchall()


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
def exists_notification(session, notification_id):
    """Helper method to check if a notification exists."""
    res = session.execute(text("""SELECT EXISTS(
                                        SELECT 1
                                          FROM public.notification
                                         WHERE id='{0}') AS notf""".format(notification_id))).fetchone()
    return res.notf


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
def exists_user_notifications(session, user_id):
    """Helper method to check if notifications for user exists."""
    res = session.execute(text("""SELECT EXISTS(
                                    SELECT 1 FROM public.notification WHERE user_id='{0}') AS user"""
                               .format(user_id))).fetchone()
    return res.user


# noinspection SqlDialectInspection,SqlNoDataSourceInspection
def delete_user_notifications(session, user_id):
    """Helper method to delete notifications for user."""
    return session.execute(text("""DELETE FROM public.notification
                                   WHERE user_id='{0}'""".format(user_id)))


# registration request creation
def create_registration(data, tracking_id):
    """ Helper method to create a registration request"""
    return RegDetails.create(data, tracking_id)


# de_registration request creation
def create_de_registration(data, tracking_id):
    """ Helper method to create a registration request"""
    return DeRegDetails.create(data, tracking_id)


def create_dummy_request(data, request_type, status='Pending Review'):
    """Helper method to create a dummy request in the database tables
    based on the request type and convert it into a input status.
    Default = Request will be in pending review
    """
    if request_type == 'Registration':
        request = create_registration(data, uuid.uuid4())
        request.update_report_file('test report')
        request.update_status(status)
        return request
    else:
        request = create_de_registration(data, uuid.uuid4())
        request.update_report_file('test report')
        request.update_status(status)
        return request


def create_processed_dummy_request(data, request_type, status='Pending Review'):
    """Helper method to create a dummy request in the database tables
    based on the request type and convert it into a input status.
    Default = Request will be in pending review
    """
    if request_type == 'Registration':
        request = create_registration(data, uuid.uuid4())
        request.update_report_file('test report')
        request.update_report_status('Processed')
        request.update_status(status)
        return request
    else:
        request = create_de_registration(data, uuid.uuid4())
        request.update_report_file('test report')
        request.update_report_status('Processed')
        request.update_status(status)
        return request


def create_assigned_dummy_request(data, request_type, reviewer_id, reviewer_name):
    """Helper method to create a dummy request in the database tables based on the
    request type and convert it into the already assigned request.
    """
    if request_type == 'Registration':
        request = create_registration(data, uuid.uuid4())
        request.update_report_file('test report')
        request.update_status('Pending Review')
        request.update_processing_status('Processed')
        request.update_report_status('Processed')
        request.update_reviewer_id(reviewer_id, reviewer_name, request.id)
        return request
    else:
        request = create_de_registration(data, uuid.uuid4())
        request.update_report_file('test report')
        request.update_status('Pending Review')
        request.update_processing_status('Processed')
        request.update_report_status('Processed')
        request.update_reviewer_id(reviewer_id, reviewer_name, request.id)
        return request


def create_dummy_devices(data, request_type, request, db=None, file_path=None, file_content=None):
    """Helper method to create a dummy request with devices and assign it to a dummy reviewer.
    based on request_type.
    """
    if request_type == 'Registration':
        data.update({'reg_details_id': request.id})
        device = RegDevice.create(data)
        device.technologies = DeviceTechnology.create(device.id, data.get('technologies'))
        Device.create(RegDetails.get_by_id(request.id), device.id)
    else:  # De-registration
        # creating sample file
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'w') as f:
            for content in file_content:
                f.write(content)
                f.write('\n')

        data = DeRegDevice.curate_args(data, request)
        imei_tac_map = Utilities.extract_imeis_tac_map(data, request)
        created = DeRegDevice.bulk_create(data, request)
        device_id_tac_map = Utilities.get_id_tac_map(created)
        for device in device_id_tac_map:
            device_imeis = imei_tac_map.get(device.get('tac'))
            dereg_imei_list = DeRegImei.get_deregimei_list(device.get('id'), device_imeis)
            db.session.execute(DeRegImei.__table__.insert(), dereg_imei_list)
    return request


def create_dummy_documents(files, request_type, request, app=None):
    """Helper method to create dummy documents for a request.
    """
    if request_type == 'Registration':
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        for file in files:
            document = Documents.get_document_by_name(file.get('label'), 1)
            reg_doc = RegDocuments(filename='{0}_{1}'.format(current_time, file.get('file_name')))
            reg_doc.reg_details_id = request.id
            reg_doc.document_id = document.id
            reg_doc.save()

            file_path = '{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id, file.get('file_name'))
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            with open(file_path, 'wb') as f:
                f.seek(1073741824-1)
                f.write(b"\0")
    else:
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        for file in files:
            document = Documents.get_document_by_name(file.get('label'), 2)
            dereg_doc = DeRegDocuments(filename='{0}_{1}'.format(current_time, file.get('file_name')))
            dereg_doc.dereg_id = request.id
            dereg_doc.document_id = document.id
            dereg_doc.save()

            file_path = '{0}/{1}/{2}'.format(app.config['DRS_UPLOADS'], request.tracking_id, file.get('file_name'))
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            with open(file_path, 'wb') as f:
                f.seek(1073741824-1)
                f.write(b"\0")
    return request
