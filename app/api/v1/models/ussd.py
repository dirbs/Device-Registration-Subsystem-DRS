"""
De Registration Details Model Module.
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

from sqlalchemy.sql import exists
from flask_babel import lazy_gettext as _

from app import db, app
from app.api.v1.models.deregcomments import DeRegComments
from app.api.v1.schema.deregdetails import DeRegDetailsSchema
from app.api.v1.models.status import Status


class UssdModel(db.Model):
    """Database model for USSD."""
    __tablename__ = 'regdetails'
    #
    # id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.String(64), nullable=False)
    # user_name = db.Column(db.String)
    # reviewer_id = db.Column(db.String(64), nullable=True)
    # reviewer_name = db.Column(db.String(64), nullable=True)
    # report_allowed = db.Column(db.Boolean, default=False)
    # device_count = db.Column(db.Integer, nullable=False)
    # imei_per_device = db.Column(db.Integer, nullable=False)
    # import_type = db.Column(db.String(10))
    # file = db.Column(db.String(30))
    # imeis = db.Column(db.String)
    # m_location = db.Column(db.String(20), nullable=False)
    # tracking_id = db.Column(db.String(64))
    # created_at = db.Column(db.DateTime(timezone=False), default=db.func.now())
    # updated_at = db.Column(db.DateTime(timezone=False), onupdate=db.func.now(), default=db.func.now())
    # processing_status = db.Column(db.Integer, db.ForeignKey('status.id'))
    # report_status = db.Column(db.Integer, db.ForeignKey('status.id'))
    # summary = db.Column(db.UnicodeText)
    # report = db.Column(db.String)
    # duplicate_imeis_file = db.Column(db.String())
    #
    # status = db.Column(db.Integer, db.ForeignKey('status.id'))
    # comments = db.relationship('RegComments', backref='regdetails', passive_deletes=True, lazy=True)
    # documents = db.relationship('RegDocuments', backref='regdetails', passive_deletes=True, lazy=True)
    # devices = db.relationship('Device', backref='regdetails', passive_deletes=True, lazy=True)
    # msisdn = db.Column(db.String(20))
    # network = db.Column(db.String(20))

    # def __init__(self, args, tracking_id):
    #     """Constructor."""
    #     status_id = Status.get_status_id('New Request')
    #
    #     self.file = args.get('file')
    #     self.device_count = args.get('device_count')
    #     self.user_id = args.get('user_id')
    #     self.user_name = args.get('user_name')
    #     self.reason = args.get('reason')
    #     self.tracking_id = tracking_id
    #     self.status = status_id
    #     self.processing_status = status_id
    #     self.report_status = status_id

    @staticmethod
    def exists(request_id):
        """Method to check weather the request exists or not."""
        return db.session.query(
            exists()
            .where(UssdModel.id == request_id)) \
            .scalar()

    @classmethod
    def get_by_id(cls, dereg_details_id):
        """Get a request details by ID."""
        return UssdModel.query.filter_by(id=dereg_details_id).first()

    @classmethod
    def get_all(cls):
        """Get all the data from the table."""
        return UssdModel.query.order_by(UssdModel.created_at.desc()).all()

