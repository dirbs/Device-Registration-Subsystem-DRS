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


class DeRegDetails(db.Model):
    """Database model for deregdetails table."""
    __tablename__ = 'deregdetails'

    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.String(64), nullable=True)
    reviewer_name = db.Column(db.String(64), nullable=True)
    report_allowed = db.Column(db.Boolean, default=False)
    file = db.Column(db.String(30))
    device_count = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(64), nullable=False)
    user_name = db.Column(db.String)
    tracking_id = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=False), default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=False), onupdate=db.func.now(), default=db.func.now())
    processing_status = db.Column(db.Integer, db.ForeignKey('status.id'))
    report_status = db.Column(db.Integer, db.ForeignKey('status.id'))
    status = db.Column(db.Integer, db.ForeignKey('status.id'))
    summary = db.Column(db.UnicodeText)
    report = db.Column(db.String)
    invalid_imeis_file = db.Column(db.String())

    comments = db.relationship('DeRegComments', backref='deregdetails', passive_deletes=True, lazy=True)
    documents = db.relationship('DeRegDocuments', backref='deregdetails', passive_deletes=True, lazy=True)
    devices = db.relationship('DeRegDevice', backref='deregdetails', passive_deletes=True, lazy=True)

    def __init__(self, args, tracking_id):
        """Constructor."""
        status_id = Status.get_status_id('New Request')

        self.file = args.get('file')
        self.device_count = args.get('device_count')
        self.user_id = args.get('user_id')
        self.user_name = args.get('user_name')
        self.reason = args.get('reason')
        self.tracking_id = tracking_id
        self.status = status_id
        self.processing_status = status_id
        self.report_status = status_id

    @classmethod
    def create_index(cls, engine):
        """ Create Indexes for De-Registration detail table class. """

        # device_count_index = db.Index('dereg_device_count', cls.device_count)
        # device_count_index.create(bind=engine)

        # tracking_id_index = db.Index('dereg_tracking_id', cls.tracking_id)
        # tracking_id_index.create(bind=engine)

        status_index = db.Index('dereg_status', cls.status, postgresql_concurrently=True)
        status_index.create(bind=engine)

        # processing_status_index = db.Index('dereg_processing_status', cls.processing_status)
        # processing_status_index.create(bind=engine)

        # report_status_index = db.Index('dereg_report_status', cls.report_status)
        # report_status_index.create(bind=engine)

        # created_at_index = db.Index('dereg_created_at', cls.created_at)
        # created_at_index.create(bind=engine)

        # updated_at_index = db.Index('dereg_updated_at', cls.updated_at)
        # updated_at_index.create(bind=engine)

    def save(self):
        """Save current model state to the table."""
        try:
            db.session.add(self)
            db.session.flush()
        except Exception as e:
            app.logger.exception(e)
            db.session.rollback()
            raise Exception

    def save_with_commit(self):
        """Save and commit current model state to the table."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def create(cls, args, tracking_id):
        try:
            """Add new request data to the table."""
            reg_request = cls(args, tracking_id)
            status_id = Status.get_status_id('New Request')
            reg_request.status = status_id
            reg_request.save()
            return reg_request
        except Exception as e:
            app.logger.exception(e)
            db.session.rollback()

    @staticmethod
    def exists(request_id):
        """Method to check weather the request exists or not."""
        return db.session.query(
            exists()
            .where(DeRegDetails.id == request_id)) \
            .scalar()

    @staticmethod
    def un_assign_request(request_id):
        """Un-assign a request."""
        request = DeRegDetails.get_by_id(request_id)
        request.reviewer_id = None
        request.reviewer_name = None
        request.status = 3

        DeRegDetails.commit_case_changes(request)

    @classmethod
    def get_by_id(cls, dereg_details_id):
        """Get a request details by ID."""
        return DeRegDetails.query.filter_by(id=dereg_details_id).first()

    @classmethod
    def get_all(cls):
        """Get all the data from the table."""
        return DeRegDetails.query.order_by(DeRegDetails.created_at.desc()).all()

    def update_status(self, status):
        """Update current status of the request."""
        self.status = Status.get_status_id(status)
        self.save()

    def update_processing_status(self, status):
        """Update current processing status of the request."""
        try:
            self.processing_status = Status.get_status_id(status)
            self.save()
        except Exception:
            raise Exception

    @classmethod
    def toggle_permission(cls, request):
        """Toggle the permission of the of user to view report"""

        request.report_allowed = not request.report_allowed
        request.save_with_commit()
        return request.report_allowed

    def update_summary(self, summary):
        """Update compliance summary of the request."""
        self.summary = json.dumps({'summary': summary})
        self.save()

    def update_report_file(self, filename):
        """Update report file name column."""
        self.report = filename
        self.save()

    def update_report_status(self, status):
        """Updates report status of the requests."""
        self.report_status = Status.get_status_id(status)
        self.save()

    @staticmethod
    def curate_args(request):
        """Curate http request args."""
        args = request.form.to_dict()
        file = request.files.get('file')
        if file:
            args.update({'file': file.filename.split("/")[-1]})
        return args

    @classmethod
    def get_update_status(cls, status):
        """Get updated status of request."""
        if status in ['Pending Review', 'Information Requested']:
            return Status.get_status_id('Pending Review')
        else:
            return None

    @classmethod
    def is_update_allowed(cls, status):
        """Check if updating the request is allowed or not."""
        restricted_status = ['In Review', 'Approved', 'Rejected', 'Closed']
        if status in restricted_status:
            return False
        else:
            return True

    @classmethod
    def close(cls, dereg_details):
        """Close currently active request."""
        closed = Status.get_status_id('Closed')
        if dereg_details.status == closed:
            return {
                'message': _('The request is already closed')
            }
        else:
            dereg_details.status = closed
            dereg_details.save_with_commit()
            return dereg_details

    @classmethod
    def update(cls, args, dereg_details, file):
        """Update current request details."""
        try:
            status = Status.get_status_type(dereg_details.status)
            processing_required = True if file else False
            if cls.is_update_allowed(status):
                if 'device_count' in args:
                    dereg_details.device_count = args.get('device_count')
                if 'file' in args:
                    dereg_details.file = args.get('file')
                if 'reason' in args:
                    dereg_details.reason = args.get('reason')
                if processing_required:
                    new_status_id = Status.get_status_id('New Request')
                    dereg_details.processing_status = new_status_id
                    dereg_details.report_status = new_status_id
                    dereg_details.summary = None
                    dereg_details.report = None
                    dereg_details.report_allowed = False
                # dereg_details.status = cls.get_update_status(status) or dereg_details.status
                dereg_details.save_with_commit()
                return dereg_details
        except Exception:
            raise Exception

    @classmethod
    def add_comment(cls, section, comment, user_id, user_name, status, request_id):
        """Method to add comment on request."""
        request = cls.get_by_id(request_id)
        DeRegComments.add(section, comment, user_id, user_name, status, request.id)
        try:
            db.session.add(request)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def update_reviewer_id(cls, reviewer_id, reviewer_name, request_id, status=4):
        """Update reviewer id of the request.

        Expected default behavior is to change request status to In-Review.
        """
        if reviewer_id and request_id:
            request = cls.get_by_id(request_id)

            # if request is already in pending state
            if request.status == 3:
                request.reviewer_id = reviewer_id
                request.reviewer_name = reviewer_name
                request.status = status
                try:
                    db.session.add(request)
                    db.session.commit()
                    return True
                except Exception:
                    db.session.rollback()
                    raise Exception
            else:
                return False

    # noinspection SqlDialectInspection,SqlNoDataSourceInspection
    @staticmethod
    def get_imeis_count(user_id):
        """Method to return total imeis count of user requests."""
        pending_query = """SELECT SUM(device_count) as pending_count
                             FROM public.deregdevice
                            WHERE dereg_details_id IN (
                                SELECT id
                                  FROM public.deregdetails
                                 WHERE (status = '3' or status = '4') AND user_id = '{0}' )""".format(user_id)

        approved_query = """SELECT SUM(device_count) as approved_count
                             FROM public.deregdevice
                            WHERE dereg_details_id IN (
                                SELECT id
                                  FROM public.deregdetails
                                 WHERE status = 6 AND user_id = '{0}' )""".format(user_id)

        rejected_query = """SELECT SUM(device_count) as rejected_count
                             FROM public.deregdevice
                            WHERE dereg_details_id IN (
                                SELECT id
                                  FROM public.deregdetails
                                 WHERE status = '7' AND user_id = '{0}' )""".format(user_id)
        try:
            pending_requests = db.engine.execute(pending_query).fetchone().pending_count
            approved_requests = db.engine.execute(approved_query).fetchone().approved_count
            rejected_requests = db.engine.execute(rejected_query).fetchone().rejected_count
            return {
                'pending_registration': pending_requests if pending_requests is not None else 0,
                'registered': approved_requests if approved_requests is not None else 0,
                'not_registered': rejected_requests if rejected_requests is not None else 0
            }
        except Exception as e:
            app.logger.error('exception encountered in deregdetails.get_imeis_count() see below:')
            app.logger.exception(e)
            return {
                'pending_registration': 0,
                'registered': 0,
                'not_registered': 0
            }

    @classmethod
    def get_section_by_state(cls, request_id, section_type):
        """Method to return most recent state of a section."""
        request = DeRegDetails.get_by_id(request_id)
        section_data = DeRegComments.get_all_by_section_type(request.id, section_type)
        if len(section_data) > 0:
            section_status = section_data[0].status
            section_type = section_type

            comments = []
            for sec in section_data:
                comment = {
                    'user_id': sec.user_id,
                    'user_name': sec.user_name,
                    'comment': sec.comment,
                    'datetime': sec.added_at
                }

                comments.append(comment)

            return {
                'section_type': section_type,
                'section_status': section_status,
                'comments': comments
            }
        else:
            return {
                'section_type': section_type,
                'section_status': None,
                'comments': None
            }

    @staticmethod
    def commit_case_changes(request):
        """Commit changes to the case object."""
        try:
            db.session.add(request)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @staticmethod
    def get_normalized_imeis(request):
        """Method to get normalized imeis of the request."""
        normalized_imeis = []
        devices = request.devices
        for device in devices:
            device_imeis = device.dereg_device_imei
            for imei in device_imeis:
                normalized_imeis.append(imei.norm_imei)

        return normalized_imeis

    @classmethod
    def get_dashboard_report(cls, user_id, user_type):
        """ Get dashboard report for de-registration"""

        if user_type != 'reviewer':
            total_count = cls.query.filter_by(user_id=user_id).count()
            new_request = cls.query.filter_by(user_id=user_id).filter_by(status=1).count()
            awaiting_document = cls.query.filter_by(user_id=user_id).filter_by(status=2).count()
            pending_review = cls.query.filter_by(user_id=user_id).filter_by(status=3).count()
            in_review = cls.query.filter_by(user_id=user_id).filter_by(status=4).count()
            information_requested = cls.query.filter_by(user_id=user_id).filter_by(status=5).count()
            approved = cls.query.filter_by(user_id=user_id).filter_by(status=6).count()
            rejected = cls.query.filter_by(user_id=user_id).filter_by(status=7).count()
            latest_req = cls.query.filter_by(user_id=user_id).filter_by(status=3).filter_by(report_status=10)\
                             .order_by(cls.created_at.desc()).all()[:10]
            latest_requests = DeRegDetailsSchema().dump(latest_req, many=True).data
            return {
                "total_requests": total_count,
                "new_requests": new_request,
                "awaiting_document": awaiting_document,
                "pending_review": pending_review,
                "in_review": in_review,
                "information_requested": information_requested,
                "approved": approved,
                "rejected": rejected,
                "latest_request": latest_requests
            }
        else:
            review_count = cls.query.filter_by(reviewer_id=user_id).filter_by(status=4).count()
            pending_review_count = cls.query.filter_by(status=3).filter_by(reviewer_id=None).count()
            pending_review_req = cls.query.filter_by(status=3).filter_by(reviewer_id=None).filter_by(report_status=10)\
                .order_by(cls.created_at.desc()).all()[:10]
            pending_review_requests = DeRegDetailsSchema().dump(pending_review_req, many=True).data
            return {
                "in_review_count": review_count,
                "pending_review_count": pending_review_count,
                "latest_pending_requests": pending_review_requests
            }
