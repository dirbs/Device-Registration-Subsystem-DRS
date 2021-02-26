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


class RegDetails(db.Model):
    """Database model for regdetails table."""
    __tablename__ = 'regdetails'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False)
    user_name = db.Column(db.String)
    reviewer_id = db.Column(db.String(64), nullable=True)
    reviewer_name = db.Column(db.String(64), nullable=True)
    report_allowed = db.Column(db.Boolean, default=False)
    device_count = db.Column(db.Integer, nullable=False)
    imei_per_device = db.Column(db.Integer, nullable=False)
    import_type = db.Column(db.String(10))
    file = db.Column(db.String(30))
    imeis = db.Column(db.String)
    m_location = db.Column(db.String(20), nullable=False)
    tracking_id = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=False), default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=False), onupdate=db.func.now(), default=db.func.now())
    processing_status = db.Column(db.Integer, db.ForeignKey('status.id'))
    report_status = db.Column(db.Integer, db.ForeignKey('status.id'))
    summary = db.Column(db.UnicodeText)
    report = db.Column(db.String)
    duplicate_imeis_file = db.Column(db.String())

    status = db.Column(db.Integer, db.ForeignKey('status.id'))
    comments = db.relationship('RegComments', backref='regdetails', passive_deletes=True, lazy=True)
    documents = db.relationship('RegDocuments', backref='regdetails', passive_deletes=True, lazy=True)
    devices = db.relationship('Device', backref='regdetails', passive_deletes=True, lazy=True)
    msisdn = db.Column(db.String(20))
    network = db.Column(db.String(20))

    def __init__(self, args, tracking_id):
        """Constructor."""
        status_id = Status.get_status_id('New Request')
        self.user_id = args.get('user_id')
        self.user_name = args.get('user_name')
        self.device_count = args.get('device_count')
        self.imei_per_device = args.get('imei_per_device')
        self.file = args.get('file')
        self.import_type = 'file' if self.file else 'webpage'
        self.imeis = '%s' % args.get('imeis')
        self.m_location = args.get('m_location')
        self.tracking_id = tracking_id
        self.status = status_id
        self.processing_status = status_id
        self.report_status = status_id
        self.msisdn = args.get("msisdn")
        self.network = args.get("network")


    @classmethod
    def create_index(cls, engine):
        """ Create Indexes for Registration Details table. """

        # reg_device_count = db.Index('reg_device_count_index', cls.device_count)
        # reg_device_count.create(bind=engine)

        # reg_imei_per_device = db.Index('reg_imei_per_device_index', cls.imei_per_device)
        # reg_imei_per_device.create(bind=engine)

        # reg_m_location = db.Index('reg_m_location_index', cls.m_location)
        # reg_m_location.create(bind=engine)

        # reg_tracking_id = db.Index('reg_tracking_id_index', cls.tracking_id)
        # reg_tracking_id.create(bind=engine)

        reg_request_status = db.Index('reg_request_status_index', cls.status, postgresql_concurrently=True)
        reg_request_status.create(bind=engine)

        # reg_processing_status = db.Index('reg_processing_status_index', cls.processing_status)
        # reg_processing_status.create(bind=engine)

        # reg_report_status = db.Index('reg_report_status_index', cls.report_status)
        # reg_report_status.create(bind=engine)

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

    @staticmethod
    def un_assign_request(request_id):
        """Un-assign a request."""
        request = RegDetails.get_by_id(request_id)
        request.reviewer_id = None
        request.reviewer_name = None
        request.status = 3

        RegDetails.commit_case_changes(request)

    @classmethod
    def create(cls, args, tracking_id):
        """Create a new registration request."""
        try:
            reg_request = cls(args, tracking_id)
            reg_request.save()
            # DeviceQuota.update_reg_quota(reg_request.user_id, int(reg_request.device_count))
            return reg_request
        except Exception:
            raise Exception

    @classmethod
    def is_update_allowed(cls, status):
        """Check if a request is allowed to be updated."""
        restricted_status = ['In Review', 'Approved', 'Rejected', 'Closed']
        if status in restricted_status:
            return False
        else:
            return True

    @classmethod
    def toggle_permission(cls, request):
        """Toggle the permission of the of user to view report"""

        request.report_allowed = not request.report_allowed
        request.save_with_commit()
        return request.report_allowed

    @classmethod
    def get_update_status(cls, status):
        """Return statue of the request."""
        if status in ['Information Requested']:
            return Status.get_status_id('In Review')
        else:
            return None

    @classmethod
    def close(cls, reg_details):
        """Close a currently active registration request."""
        closed = Status.get_status_id('Closed')
        if reg_details.status == closed:
            return {
                'message': _('The request is already closed')
            }
        else:
            reg_details.status = closed
            reg_details.save_with_commit()
            return reg_details

    @classmethod
    def update(cls, args, reg_details, request_file):
        """Update current regsitration request."""
        try:
            status = Status.get_status_type(reg_details.status)
            is_processing_needed = True if request_file or 'imeis' in args else False
            if cls.is_update_allowed(status):
                if 'device_count' in args:
                    reg_details.device_count = args.get('device_count')
                if 'imei_per_device' in args:
                    reg_details.imei_per_device = args.get('imei_per_device')
                if 'file' in args:
                    reg_details.file = args.get('file')
                if 'imeis' in args:
                    reg_details.imeis = '%s' % args.get('imeis')
                if 'm_location' in args:
                    reg_details.m_location = args.get('m_location')
                # else:
                #    reg_details.status = cls.get_update_status(status) or reg_details.status
                if is_processing_needed:
                    new_status_id = Status.get_status_id('New Request')
                    reg_details.processing_status = new_status_id
                    reg_details.report_status = new_status_id
                    reg_details.report = None
                    reg_details.summary = None
                    reg_details.report_allowed = False
                reg_details.save()
                return reg_details
        except Exception:
            raise Exception

    @staticmethod
    def get_by_id(reg_details_id):
        """Return registration request by id."""
        if reg_details_id:
            return RegDetails.query.filter_by(id=reg_details_id).first()
        else:
            return None

    @staticmethod
    def exists(request_id):
        """Method to check weather the record exists or not."""
        return db.session.query(
            exists()
            .where(RegDetails.id == request_id)) \
            .scalar()

    @staticmethod
    def get_by_status(status):
        """Returns Registration/De-Registration Requests by Status."""
        if status:
            return RegDetails.query.filter_by(status=status).all()
        return None

    def update_summary(self, summary):
        """Update compliance summary of the request."""
        self.summary = json.dumps({'summary': summary})
        self.save()

    def update_report_file(self, filename):
        """Update compliance report of the request."""
        self.report = filename
        self.save()

    @staticmethod
    def get_all():
        """Return all registration requests."""
        return RegDetails.query.order_by(RegDetails.created_at.desc()).all()

    @classmethod
    def update_reviewer_id(cls, reviewer_id, reviewer_name, request_id, status=4):
        """Updates Reviewer Id of request.

        Expected default behavior is to change request status to In-Review,
        But can be used to change status to something else.
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

    @classmethod
    def add_comment(cls, section, comment, user_id, user_name, status, request_id):
        """Method to add comment on request."""
        request = cls.get_by_id(request_id)
        RegComments.add(section, comment, user_id, user_name, status, request.id)
        try:
            db.session.add(request)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def get_devices(cls, request_id):
        """Method to get device details from request."""
        request = cls.get_by_id(request_id)
        return request.devices

    def update_status(self, status):
        """Update status of the request."""
        self.status = Status.get_status_id(status)
        self.save()

    def update_processing_status(self, status):
        """Updates processing status of the requests."""
        self.processing_status = Status.get_status_id(status)
        self.save()

    def update_report_status(self, status):
        """Updates report status of the requests."""
        self.report_status = Status.get_status_id(status)
        self.save()

    def update_statuses(self, status):
        """Update reporting and processing status."""
        status_id = Status.get_status_id(status)
        self.processing_status = status_id
        self.report_status = status_id
        self.save_with_commit()

    @staticmethod
    def curate_args(request):
        """Curate args for the request."""
        args = request.form.to_dict()
        file = request.files.get('file')
        if file:
            args.update({'file': file.filename.split("/")[-1]})
        return args

    @staticmethod
    def get_normalized_imeis(request):
        """Method to return normalized imeis of a request."""
        normalized_imeis = []
        devices = request.devices
        for device in devices:
            device_imeis = device.imeis
            for imei in device_imeis:
                normalized_imeis.append(imei.normalized_imei)
        return normalized_imeis

    @staticmethod
    def get_duplicate_imeis(request):
        """Method for check if imeis are duplicated and return duplicated imeis."""
        normalized_imeis = RegDetails.get_normalized_imeis(request)
        if len(normalized_imeis) > 1:
            duplicate_imei_query = text("""SELECT imei as imei_norm FROM
                                        (SELECT imei FROM public.approvedimeis WHERE removed IS NOT TRUE
                                            AND status = 'whitelist') 
                                            AS approved_imeis 
                                            WHERE imei IN {imei_list}""".format(imei_list=tuple(normalized_imeis)))
        else:
            duplicate_imei_query = text("""SELECT imei as imei_norm FROM
                                        (SELECT imei FROM public.approvedimeis WHERE removed IS NOT TRUE
                                            AND status = 'whitelist') 
                                            AS approved_imeis 
                                            WHERE imei = '{imei_list}'::text""".format(imei_list=normalized_imeis[0]))
        res = db.engine.execute(duplicate_imei_query).fetchall()
        result = list(chain.from_iterable(res))
        return result

    # noinspection SqlNoDataSourceInspection,SqlDialectInspection
    @staticmethod
    def get_imeis_count(user_id):
        """Method to return total imeis count of user requests."""
        query = """SELECT status, SUM(device_count * imei_per_device) AS imei_count
                     FROM public.regdetails
                    WHERE user_id='{0}' GROUP BY status""".format(user_id)
        try:
            res = db.engine.execute(query).fetchall()
            res = dict(res)

            return {
                'pending_registration': res.get(3, 0) + res.get(4, 0),
                'registered': res.get(6, 0),
                'not_registered': res.get(7, 0)
            }
        except Exception as e:
            app.logger.error('exception encountered in regdetails.get_imeis_count() see below:')
            app.logger.exception(e)
            return {
                'pending_registration': 0,
                'registered': 0,
                'not_registered': 0
            }

    @classmethod
    def get_section_states(cls, request_id):
        """Method to return most recent state of the review-sections."""
        request = RegDetails.get_by_id(request_id)
        sections = RegComments.get_all_by_regid(request.id)
        return sections

    @classmethod
    def get_section_by_state(cls, request_id, section_type):
        """Method to return most recent state of a section"""
        request = RegDetails.get_by_id(request_id)
        section_data = RegComments.get_all_by_section_type(request.id, section_type)

        # return data of latest section status
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

    @classmethod
    def get_dashboard_report(cls, user_id, user_type):
        """ Fetch all the registration reports data"""

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
            latest_requests = RegistrationDetailsSchema().dump(latest_req, many=True).data
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
            pending_review_req = cls.query.filter_by(status=3).filter_by(report_status=10)\
                .filter_by(reviewer_id=None).order_by(cls.created_at.desc()).all()[:10]
            pending_review_requests = RegistrationDetailsSchema().dump(pending_review_req, many=True).data
            return {
                "in_review_count": review_count,
                "pending_review_count": pending_review_count,
                "latest_pending_requests": pending_review_requests
            }

    @classmethod
    def get_count(cls, msisdn):
        count_with_msisdn = cls.query.filter_by(msisdn=msisdn).count()
        return {
            "count_with_msisdn": count_with_msisdn
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
