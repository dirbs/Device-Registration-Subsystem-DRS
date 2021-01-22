"""
DRS De-Registration Device Model package.
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
from app import db, app
from app.api.v1.models.deregimei import DeRegImei
from app.api.v1.helpers.utilities import Utilities
import json
import threading
from app.api.v1.models.deregdetails import DeRegDetails


class DeRegDevice(db.Model):
    """Database model for deregdevice table."""
    __tablename__ = 'deregdevice'

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(1000))
    model_name = db.Column(db.String(1000), nullable=False)
    model_num = db.Column(db.String(1000), nullable=False)
    operating_system = db.Column(db.String(1000), nullable=False)
    device_type = db.Column(db.String(1000), nullable=False)
    technology = db.Column(db.String(1000), nullable=False)
    device_count = db.Column(db.Integer, nullable=False)
    tac = db.Column(db.String(8))

    dereg_details_id = db.Column(db.Integer, db.ForeignKey('deregdetails.id'))
    dereg_device_imei = db.relationship('DeRegImei', backref='deregdevice', passive_deletes=True, lazy=True)

    def __init__(self, args):
        """Constructor."""
        self.brand = args.get('brand_name')
        self.model_name = args.get('model_name')
        self.model_num = args.get('model_num')
        self.operating_system = args.get('operating_system')
        self.device_type = args.get('device_type')
        self.technology = args.get('technology')
        self.device_count = args.get('count')
        self.tac = args.get('tac')

    @classmethod
    def create_index(cls, engine):
        """ Create Indexes for De-Registration device table. """

        # brand_index = db.Index('dereg_device_brand', cls.brand)
        # brand_index.create(bind=engine)

        # model_name_index = db.Index('dereg__device_model_name', cls.model_name)
        # model_name_index.create(bind=engine)

        # model_number_index = db.Index('dereg_device_model_number', cls.model_num)
        # model_number_index.create(bind=engine)

        # operating_system_index = db.Index('dereg_device_os', cls.operating_system)
        # operating_system_index.create(bind=engine)

        # device_type_index = db.Index('dereg_device_type', cls.device_type)
        # device_type_index.create(bind=engine)

        # technology_index = db.Index('dereg_device_technology', cls.technology)
        # technology_index.create(bind=engine)

        # tac_index = db.Index('dereg_device_tac', cls.tac)
        # tac_index.create(bind=engine)

    @classmethod
    def curate_args(cls, args, dereg):
        """Curate http request args."""
        if 'devices' in args:
            args['devices'] = json.loads(args.get('devices', []))
        if dereg:
            args['dereg_id'] = dereg.id
        else:
            args['dereg_id'] = ''
        return args

    @classmethod
    def create(cls, args, dereg_id):
        """Create a new de registration device."""
        device = DeRegDevice(args)
        device.dereg_details_id = dereg_id
        device.save()
        return device

    @classmethod
    def bulk_insert_imeis(cls, devices, imei_tac_map, old_devices, imeis_list, dereg):
        """Insert IMEIs in bulk."""
        try:
            dereg.update_processing_status('Processing')
            db.session.commit()
            thread = threading.Thread(daemon=True, target=cls.async_create, args=(devices, imei_tac_map, old_devices,
                                                                                  dereg.id, imeis_list, app))
            thread.start()
        except Exception as e:
            app.logger.exception(e)
            dereg.update_processing_status('Failed')
            db.session.commit()

    @classmethod
    def bulk_create(cls, args, dereg):
        """Create devices in bulk."""
        created_devices = []
        for device_arg in args.get('devices'):
            device = cls.create(device_arg, dereg.id)
            created_devices.append(device)
        return created_devices

    @classmethod
    def async_create(cls, devices, imei_tac_map, old_devices, dereg_id, imeis_list, app):
        """Async create a new device."""
        with app.app_context():
            from app import db
            dereg = DeRegDetails.get_by_id(dereg_id)
            try:
                DeRegDevice.clear_devices(old_devices)
                for device in devices:
                    device_imeis = imei_tac_map.get(device.get('tac'))
                    dereg_imei_list = DeRegImei.get_deregimei_list(device.get('id'), device_imeis)
                    res = db.engine.execute(DeRegImei.__table__.insert(), dereg_imei_list)
                    res.close()
                dereg.update_processing_status('Processed')
                db.session.commit()
                task_id = Utilities.generate_summary(imeis_list, dereg.tracking_id)
                if task_id:
                    Utilities.pool_summary_request(task_id, dereg, app)
                else:
                    dereg.update_processing_status('Failed')
                    db.session.commit()

                if app.config['AUTOMATE_IMEI_CHECK']:
                    if DeRegDevice.auto_approve(task_id, dereg):
                        print("Auto Approved/Rejected DeRegistration Application Id:" + str(dereg.id))

            except Exception as e:
                app.logger.exception(e)
                db.session.rollback()
                dereg.update_processing_status('Failed')
                dereg.update_report_status('Failed')
                db.session.commit()

    @staticmethod
    def auto_approve(task_id, reg_details):
        # TODO: Need to remove duplicated session which throws warning
        from app.api.v1.resources.reviewer import SubmitReview
        from app.api.v1.models.devicequota import DeviceQuota as DeviceQuotaModel
        from app.api.v1.models.status import Status
        from app.api.v1.models.eslog import EsLog
        import json
        sr = SubmitReview()

        try:
            result = Utilities.check_request_status(task_id)
            section_status = 6
            sections_comment = "Auto"
            auto_approved_sections = ['device_quota', 'device_description', 'imei_classification',
                                      'imei_registration']

            if result:
                if result['non_compliant'] != 0 or result['stolen'] != 0 or result['compliant_active'] != 0 \
                        or result['provisional_non_compliant'] != 0:
                    sections_comment = sections_comment + ' Rejected, Device/s found in Non-Compliant State'
                    status = 'Rejected'
                    section_status = 7
                    message = 'Your request {id} has been rejected because Non-Compliant Device Found in it.'.format(id=reg_details.id)
                else:
                    sections_comment = sections_comment + ' Approved'
                    status = 'Approved'
                    message = 'Your request {id} has been Approved'.format(id=reg_details.id)

                if status == 'Approved':
                    # checkout device quota
                    imeis = DeRegDetails.get_normalized_imeis(reg_details)
                    user_quota = DeviceQuotaModel.get(reg_details.user_id)
                    current_quota = user_quota.reg_quota
                    user_quota.reg_quota = current_quota - len(imeis)
                    DeviceQuotaModel.commit_quota_changes(user_quota)
                    imeis = DeRegDetails.get_normalized_imeis(reg_details)

                    Utilities.de_register_imeis(imeis)

                    for section in auto_approved_sections:
                        DeRegDetails.add_comment(section, sections_comment, reg_details.user_id, 'Auto Reviewed'
                                                 , section_status, reg_details.id)

                sr._SubmitReview__generate_notification(user_id=reg_details.user_id, request_id=reg_details.id,
                                                        request_type='de-registration', request_status=section_status,
                                                        message=message)

                reg_details.summary = json.dumps({'summary': result})
                reg_details.report = result.get('compliant_report_name')
                reg_details.update_report_status('Processed')
                reg_details.update_status(status)
                reg_details.report_allowed = True
                reg_details.save()
                db.session.commit()
                # create log
                log = EsLog.auto_review(reg_details, "De-Registration Request", 'Post', status)
                EsLog.insert_log(log)
                return True
            else:
                reg_details.update_processing_status('Failed')
                reg_details.update_report_status('Failed')
                reg_details.update_status('Failed')
                db.session.commit()
                log = EsLog.auto_review(reg_details, "De-Registration Request", 'Post',
                                        Status.get_status_type(reg_details.status))
                EsLog.insert_log(log)

        except Exception as e: # pragma: no cover
            app.logger.exception(e)
            db.session.rollback()
            reg_details.update_processing_status('Failed')
            reg_details.update_status('Failed')
            message = 'Your request {id} has failed please re-initiate device request'.format(id=reg_details.id)
            sr._SubmitReview__generate_notification(user_id=reg_details.user_id, request_id=reg_details.id,
                                                    request_type='registration', request_status=7,
                                                    message=message)
            db.session.commit()
            # create log
            log = EsLog.auto_review(reg_details, "De-Registration Request", 'Post',
                                    Status.get_status_type(reg_details.status))
            EsLog.insert_log(log)

    def save(self):
        """Save the current state of the model."""
        try:
            db.session.add(self)
            db.session.flush()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def get_devices_by_dereg_id(cls, dreg_id):
        """Get devices by de registration request id."""
        devices = cls.query.filter_by(dereg_details_id=dreg_id).all()
        return devices

    @classmethod
    def get_devices_id_by_dereg_id(cls, dreg_id):
        """Get devices ids by request id."""
        devices = cls.query.filter_by(dereg_details_id=dreg_id).all()
        devices_ids = list(map(lambda x: x.id, devices))
        return devices_ids

    @classmethod
    def clear_devices(cls, old_devices):
        """Clear old devices of the request."""
        # device_ids = map(lambda device: device.id, old_devices)
        stmt = cls.__table__.delete().where(cls.id.in_(old_devices))
        res = db.engine.execute(stmt)
        res.close()

    @classmethod
    def get_by_id(cls, dereg_device_id):
        """Get device by id."""
        return cls.query.filter_by(id=dereg_device_id).first()
