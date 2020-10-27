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


class ImeiAssociation(db.Model):
    """Database Model for IMEI association/de-association Table."""
    __tablename__ = 'associatedimeis'

    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(14), nullable=False)
    uid = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, server_default=db.func.now())
    end_date = db.Column(db.DateTime, server_default=None)
    duplicate = db.Column(db.Boolean, nullable=False)
    exported_at = db.Column(db.DateTime, server_default=None)
    exported = db.Column(db.Boolean, nullable=False)

    def __init__(self, imei, uid, duplicate=False, exported=False):
        """Constructor
        Default exported=False
        First time imei is not exported
        """
        self.imei = imei
        self.uid = uid
        self.duplicate = duplicate
        self.exported = exported

    def add(self):
        """Method to insert data into associated imei."""
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise SQLAlchemyError

    @staticmethod
    def get_imei_by_uid(uid):
        """Method to list of IMEIs associated with given uid."""
        return ImeiAssociation.query.filter_by(uid=uid).filter_by(end_date=None).all()

    @staticmethod
    def get_imei(imei):
        """Method to get single imei."""
        return ImeiAssociation.query.filter_by(imei=imei).first()

    @staticmethod
    def detect_duplicate(imei, uid):
        """Method to check if imei already associated with given uid"""
        if ImeiAssociation.query.filter_by(imei=imei).filter_by(uid=uid).filter_by(end_date=None).first():
            return True
        return False

    @staticmethod
    def exists(imei_norm):
        """Check if an imei exists"""
        if ImeiAssociation.get_imei(imei_norm):
            return True
        return False

    @staticmethod
    def associated(imei_norm):
        """Check if an imei exists"""
        if ImeiAssociation.query.filter_by(imei=imei_norm).filter_by(end_date=None).first():
            return True
        return False

    @staticmethod
    def deassociate(imei, uid):
        """Method to de-associate IMEI from given uid"""
        try:
            exists = ImeiAssociation.query.filter_by(imei=imei).filter_by(uid=uid).order_by(ImeiAssociation.start_date.desc()).first()
            if exists:
                if exists.end_date is None:
                    exists.end_date = db.func.now()
                    db.session.commit()
                    return 200
                else:
                    return 406
            else:
                return 409
        except Exception:
            db.session.rollback()
            raise Exception

    @staticmethod
    def update_export_date(id):
        """Method to update exported_at when IMEI is exported"""
        try:
            associated_imeis = ImeiAssociation.query.filter_by(id=id).first()
            associated_imeis.exported_at = db.func.now()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @staticmethod
    def mark_exported(id):
        """Method to mark IMEI as exported"""
        try:
            exported_imei = ImeiAssociation.query.filter_by(id=id).first()
            exported_imei.exported_at = db.func.now()
            exported_imei.exported = True
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @staticmethod
    def get_all_imeis():
        """Method to get list of all IMEIs"""
        query = 'select * from public.associatedimeis'
        results = db.engine.execute(query)
        return results

    @staticmethod
    def bulk_exists(imeis):
        response = ImeiAssociation.query.filter_by(end_date=None).filter(ImeiAssociation.imei.in_(imeis)).count()
        return response