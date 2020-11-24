"""
DRS Approved Imeis Model package.
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

from app import db


class ApprovedImeis(db.Model):
    """Database Model for ApprovedIMEIs Table."""
    __tablename__ = 'approvedimeis'

    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(14), nullable=False)
    request_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=True)
    delta_status = db.Column(db.String(20), nullable=True)
    exported = db.Column(db.Boolean, nullable=False)
    exported_at = db.Column(db.DateTime, nullable=True)
    removed = db.Column(db.Boolean, nullable=False)
    added_at = db.Column(db.Date, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, imei_norm, request_id, status, delta_status, exported=False, removed=False):
        """Constructor

        Default exported=False & removed=False
        First time imei is neither removed nor exported
        """
        self.imei = imei_norm
        self.request_id = request_id
        self.status = status
        self.delta_status = delta_status
        self.exported = exported
        self.removed = removed

    @classmethod
    def create_index(cls, engine):
        """ Create Indexes for approved Imeis class. """

        request_index = db.Index('approved_imeis_request_id', cls.request_id, postgresql_concurrently=True)
        request_index.create(bind=engine)

        imei_index = db.Index('approved_imeis', cls.imei, postgresql_concurrently=True)
        imei_index.create(bind=engine)

        delta_index = db.Index('approved_imeis_delta', cls.delta_status, postgresql_concurrently=True)
        delta_index.create(bind=engine)

        status_index = db.Index('approved_imeis_status', cls.status, postgresql_concurrently=True)
        status_index.create(bind=engine)

        # removed_flag_index = db.Index('approved_imeis_removed', cls.removed, postgresql_concurrently=True)
        # removed_flag_index.create(bind=engine)

    def add(self):
        """Method to insert data into approved imei."""
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise SQLAlchemyError

    @staticmethod
    def get_imei(imei_norm):
        """Method to get a single imei."""
        return ApprovedImeis.query.filter_by(imei=imei_norm).filter_by(removed=False).first()

    @staticmethod
    def get_request_imeis(request_id):
        """Method to get all imeis associated to a request id."""
        return ApprovedImeis.query.filter_by(request_id=request_id).filter_by(removed=False).all()

    @staticmethod
    def exists(imei_norm):
        """Check if an imei exists"""
        if ApprovedImeis.get_imei(imei_norm):
            return True
        return False

    @staticmethod
    def registered(imei_norm):
        """Check if an imei exists and registered"""
        if ApprovedImeis.query.filter_by(imei=imei_norm).filter_by(status='whitelist').first():
            return True
        return False

    @staticmethod
    def bulk_insert_imeis(imeis):
        """Method to insert imeis in bulk, expects list of imei objects."""
        try:
            db.session.add_all(imeis)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise SQLAlchemyError

    @staticmethod
    def bulk_delete_imeis(reg_details):
        """Method to delete IMEIs in bulk."""
        approved_imeis = ApprovedImeis.query.filter_by(request_id=reg_details.id).all()
        approved_imeis_ids = map(lambda approved_imei: approved_imei.id, approved_imeis)
        stmt = ApprovedImeis.__table__.delete().where(ApprovedImeis.id.in_(approved_imeis_ids))
        res = db.engine.execute(stmt)
        res.close()

    @staticmethod
    def imei_to_export():
        """Method to return imeis that needs to be exported along with make, model, model_number etc
           based on type of the list generation.
        """
        return ApprovedImeis.query.filter_by(removed=False).all()
