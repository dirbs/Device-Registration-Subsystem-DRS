"""
DRS Registration Details Model package.
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
import json

from app import db, app
from sqlalchemy.sql import exists
from sqlalchemy import text
from itertools import chain
from flask_babel import lazy_gettext as _

from app.api.v1.helpers.utilities import Utilities
from app.api.v1.models.regcomments import RegComments
from app.api.v1.models.regdocuments import RegDocuments
from app.api.v1.models.devicequota import DeviceQuota
from app.api.v1.models.status import Status
from app.api.v1.models.approvedimeis import ApprovedImeis
from app.api.v1.schema.regdetails import RegistrationDetailsSchema


class Assembled_devices(db.Model):
    """Database model for regdetails table."""
    __tablename__ = 'assembled_devices'

    id = db.Column(db.Integer, primary_key=True)
    parent_reg_id = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.String(64), nullable=False)
    user_name = db.Column(db.String(300), nullable=False)
    device_count = db.Column(db.Integer, nullable=False)
    imei_per_device = db.Column(db.Integer, nullable=False)
    file = db.Column(db.String(300))
    tracking_id = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=False), default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=False), onupdate=db.func.now(), default=db.func.now())

    def __init__(self, args, tracking_id):
        """Constructor."""
        self.user_id = args.get('user_id')
        self.user_name = args.get('user_name')
        self.parent_reg_id = args.get('parent_id')
        self.tracking_id = tracking_id
        self.device_count = args.get('device_count')
        self.imei_per_device = args.get('imei_per_device')
        self.file = args.get('file')

    @classmethod
    def create_index(cls, engine):
        """ Create Indexes for Registration Details table. """

        reg_request_status = db.Index('assembled_devices_tracking_id_index', cls.tracking_id, postgresql_concurrently=True)
        reg_request_status.create(bind=engine)


    def save(self):
        """Save current state of the model."""
        try:
            db.session.add(self)
            db.session.flush()
        except Exception:
            db.session.rollback()
            raise Exception

    def save_with_commit(self):
        """Save and commit current state of the model."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @staticmethod
    def commit_case_changes(request):
        """Commit changes to the case with case object."""
        try:
            db.session.add(request)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception


    @classmethod
    def create(cls, args, tracking_id):
        """Create a new registration request."""
        try:
            reg_request = cls(args, tracking_id)
            reg_request.save()
            reg_request.imeis = None
            return reg_request
        except Exception:
            raise Exception

    @staticmethod
    def get_by_id(reg_id):
        """Return registration request by id."""
        if reg_id:
            return Assembled_devices.query.filter_by(id=reg_id).first()
        else:
            return None

    @staticmethod
    def get_by_parent_id(parent_id):
        """Return registration request by id."""
        if parent_id:
            return Assembled_devices.query.filter_by(parent_reg_id=parent_id).first()
        else:
            return None


    @staticmethod
    def exists(request_id):
        """Method to check weather the record exists or not."""
        return db.session.query(
            exists()
            .where(Assembled_devices.id == request_id)) \
            .scalar()

    @staticmethod
    def parent_exists(parent_reg_id):
        """Method to check weather the record exists or not."""
        return db.session.query(
            exists()
            .where(Assembled_devices.parent_reg_id == parent_reg_id)) \
            .scalar()

    @staticmethod
    def get_all():
        """Return all registration requests."""
        return Assembled_devices.query.order_by(Assembled_devices.created_at.desc()).all()

    @classmethod
    def get_child_record_with_id(cls, request_id):
        """Method to get device details from request."""

        res = cls.get_by_id(request_id)
        if res:
            data = cls.serialize_data(res)
        else:
            data = None
        return data

    @classmethod
    def get_child_records_with_parent_id(cls, parent_reg_id):
        """Method to get assembled devices with parent."""
        res_with_parent_id = Assembled_devices.query.filter_by(parent_reg_id=parent_reg_id).all()
        data_list = []
        for reg_child_device in res_with_parent_id:
            serialized_data = cls.serialize_data(reg_child_device)

            if serialized_data:
                data_list.append(serialized_data)

        if data_list:
            return data_list
        else:
            return None

    @staticmethod
    def serialize_data(request):
        data = {}

        data.update({"id": request.id})
        data.update({"parent_reg_id": request.parent_reg_id})
        data.update({"user_id": request.user_id})
        data.update({"user_name": request.user_name})
        data.update({"device_count": request.device_count})
        data.update({"imei_per_device": request.imei_per_device})
        data.update({"file": request.file})
        data.update({"tracking_id": request.tracking_id})
        data.update({"created_at": str(request.created_at)})
        data.update({"updated_at": str(request.updated_at)})
        return data

    @classmethod
    def get_child_record_with_parent_id(cls, request_id):
        """Method to get device details from request."""
        request = cls.get_by_parent_id(request_id)
        return request.devices

    @classmethod
    def get_child_applications_count(cls, parent_id):
        count_with_parent_id = cls.query.filter_by(parent_reg_id=parent_id).count()
        return {
            "count_with_parent_id": count_with_parent_id
        }

    @classmethod
    def get_all_counts(cls, msisdn):
        review_count = cls.query.filter_by(msisdn=msisdn).filter_by(status=4).count()
        pending_review_count = cls.query.filter_by(msisdn=msisdn).filter_by(status=3).count()
        approved_count = cls.query.filter_by(msisdn=msisdn).filter_by(status=6).count()
        rejected_count = cls.query.filter_by(msisdn=msisdn).filter_by(status=7).count()
        failed_count = cls.query.filter_by(msisdn=msisdn).filter_by(status=9).count()

        return {
            "review_count": review_count,
            "pending_review_count": pending_review_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "failed_count": failed_count
        }

    @staticmethod
    def bulk_update_approved_imeis(imeis, request_id, status='whitelist'):

        """Method to update the IMEIs to whitelist on child request."""
        separator = "', '"
        normalized_imei_string = "'" + separator.join(imeis) + "'"

        # print("Bulk whitelisted IMEIs")
        # print(normalized_imei_string)

        query = """update approvedimeis set status='{0}' where imei in ({1}) and request_id='{2}' and status='pending'""".format(status, normalized_imei_string, request_id)

        # print("showing the query")
        # print(query)
        res = db.engine.execute(query)

        return res
