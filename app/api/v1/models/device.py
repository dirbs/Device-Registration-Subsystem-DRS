"""
DRS Registration Device Model package.
Copyright (c) 2018-2019 Qualcomm Technologies, Inc.
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
import ast
import threading

from app import db
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.models.approvedimeis import ApprovedImeis
from app.api.v1.models.imeidevice import ImeiDevice


class Device(db.Model):
    """Database model for device table."""
    __tablename__ = 'device'

    id = db.Column(db.Integer, primary_key=True)
    tac = db.Column(db.String(8))
    reg_details_id = db.Column(db.Integer, db.ForeignKey('regdetails.id', ondelete='CASCADE'))
    reg_device_id = db.Column(db.Integer, db.ForeignKey('regdevice.id', ondelete='CASCADE'))

    imeis = db.relationship('ImeiDevice', backref='device', passive_deletes=True, lazy=True)

    def __init__(self, tac,  reg_details_id, reg_device_id):
        """Constructor."""
        self.tac = tac
        self.reg_details_id = reg_details_id
        self.reg_device_id = reg_device_id

    @classmethod
    def create_index(cls, engine):
        """ Create Indexes for Registration device table. """

        # reg_tac = db.Index('reg_tac_index', cls.tac)
        # reg_tac.create(bind=engine)

    @classmethod
    def async_bulk_create(cls, reg_details, reg_device_id, app):   # pragma: no cover
        """Create devices async."""
        with app.app_context():
            from app import db
            try:
                filename = reg_details.file
                tracking_id = reg_details.tracking_id
                args = {'imei_per_device': reg_details.imei_per_device, 'device_count': reg_details.device_count}
                response = Utilities.process_reg_file(filename, tracking_id, args)
                imeis = []
                for device_imeis in response:
                    tac = Utilities.get_imei_tac(device_imeis[0])
                    device = cls(tac, reg_details.id, reg_device_id)
                    db.session.add(device)
                    db.session.flush()
                    imeis = imeis + device_imeis
                    for imei in device_imeis:
                        imei_device = ImeiDevice(imei, device.id)
                        db.session.add(imei_device)
                        imei_object = ApprovedImeis.query.filter_by(imei=imei[:14]).first()
                        if not imei_object:
                            approved_imei = ApprovedImeis(imei[:14], reg_details.id, 'pending', 'add')
                            db.session.add(approved_imei)
                        elif imei_object and imei_object.status == 'removed':
                            imei_object.status = 'pending'
                            imei_object.removed = False
                            imei_object.request_id = reg_details.id
                            db.session.add(imei_object)
                db.session.commit()
                reg_details.update_processing_status('Processed')
                db.session.commit()
                task_id = Utilities.generate_summary(imeis, reg_details.tracking_id)
                app.logger.info('task with task_id: {0} initiated'.format(task_id))
                if not task_id:
                    reg_details.update_report_status('Failed')
                    app.logger.info('task with task_id: {0} failed'.format(task_id))
                    db.session.commit()
                else:
                    Utilities.pool_summary_request(task_id, reg_details, app)
            except Exception as e:
                app.logger.exception(e)
                db.session.rollback()
                reg_details.update_report_status('Failed')
                reg_details.update_processing_status('Failed')
                db.session.commit()
                raise e

    @classmethod
    def sync_bulk_create(cls, reg_details, reg_device_id, app):
        """Create devices in bulk."""
        try:
            flatten_imeis = []
            imeis_lists = ast.literal_eval(reg_details.imeis)
            for device_imeis in imeis_lists:
                device = cls(device_imeis[0][:8], reg_details.id, reg_device_id)
                device.save()
                for imei in device_imeis:
                    flatten_imeis.append(imei)
                    imei_device = ImeiDevice(imei, device.id)
                    db.session.add(imei_device)
                    imei_object = ApprovedImeis.query.filter_by(imei=imei[:14]).first()
                    if not imei_object:
                        approved_imei = ApprovedImeis(imei[:14], reg_details.id, 'pending', 'add')
                        db.session.add(approved_imei)
                    elif imei_object and imei_object.status == 'removed':
                        imei_object.status = 'pending'
                        imei_object.removed = False
                        imei_object.request_id = reg_details.id
                        db.session.add(imei_object)
            reg_details.update_processing_status('Processed')
            reg_details.update_report_status('Processing')
            db.session.commit()

            task_id = Utilities.generate_summary(flatten_imeis, reg_details.tracking_id)
            if task_id:
                Utilities.pool_summary_request(task_id, reg_details, app)
            else:
                reg_details.update_report_status('Failed')
                db.session.commit()
        except Exception:  # pragma: no cover
            reg_details.update_processing_status('Failed')
            db.session.commit()

    @classmethod
    def create(cls, reg_details, reg_device_id):
        """Create a new device for a request."""
        from app import app
        try:
            reg_details.update_processing_status('Processing')
            db.session.commit()
            cls.bulk_delete(reg_details)
            ApprovedImeis.bulk_delete_imeis(reg_details)
            if reg_details.import_type == 'file':
                thread = threading.Thread(daemon=True, target=cls.async_bulk_create,
                                          args=(reg_details, reg_device_id, app))
                thread.start()
            else:
                cls.sync_bulk_create(reg_details, reg_device_id, app)
        except Exception as e:   # pragma: no cover
            app.logger.exception(e)
            reg_details.update_processing_status('Failed')
            db.session.commit()

    def save(self):
        """Save the current state of the model."""
        try:
            db.session.add(self)
            db.session.flush()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def get_device_by_registration_id(cls, reg_id):
        """Get device by request id."""
        device = cls.query.filter_by(reg_details_id=reg_id).first()
        return device

    @classmethod
    def bulk_delete(cls, regdetails):
        """Delete devices of a request in bulk."""
        device_ids = map(lambda device: device.id, regdetails.devices)
        stmt = cls.__table__.delete().where(cls.id.in_(device_ids))
        res = db.engine.execute(stmt)
        res.close()
