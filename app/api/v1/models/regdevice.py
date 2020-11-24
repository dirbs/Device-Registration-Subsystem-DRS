"""
DRS Registration Reg-Device Model package.
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
from app import db

from app.api.v1.models.status import Status
from app.api.v1.models.devicetechnology import DeviceTechnology
from app.api.v1.models.devicetype import DeviceType
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.models.device import Device


class RegDevice(db.Model):
    """Database model for regdevice table."""
    __tablename__ = 'regdevice'

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(1000), nullable=False)
    model_name = db.Column(db.String(1000), nullable=False)
    model_num = db.Column(db.String(1000), nullable=False)
    operating_system = db.Column(db.String(1000), nullable=False)

    device_types_id = db.Column(db.Integer, db.ForeignKey('devicetype.id'))
    reg_details_id = db.Column(db.Integer, db.ForeignKey('regdetails.id', ondelete='CASCADE'))
    device_technologies = db.relationship('DeviceTechnology', backref='regdevice', passive_deletes=True, lazy=True)

    def __init__(self, args):
        """Constructor."""
        self.brand = args.get('brand')
        self.model_name = args.get('model_name')
        self.model_num = args.get('model_num')
        self.operating_system = args.get('operating_system')

    @classmethod
    def create_index(cls, engine):
        """ Create Indexes for Registration Device table. """

        # reg_device_brand = db.Index('reg_device_brand_index', cls.brand)
        # reg_device_brand.create(bind=engine)

        # reg_device_model_name = db.Index('reg_device_model_name_index', cls.model_name)
        # reg_device_model_name.create(bind=engine)

        # reg_device_model_num = db.Index('reg_device_model_num_index', cls.model_num)
        # reg_device_model_num.create(bind=engine)

        # reg_device_os = db.Index('reg_device_os_index', cls.operating_system)
        # reg_device_os.create(bind=engine)

    def save(self):
        """Save the current state of the model."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def create(cls, args):
        """Create a new registration device."""
        try:
            reg_device = cls(args)
            device_type = DeviceType.get_device_type_id(args.get('device_type'))
            reg_device.device_types_id = device_type
            reg_device.reg_details_id = args.get('reg_details_id')
            reg_device.save()
            return reg_device
        except Exception:
            raise Exception

    @classmethod
    def update(cls, reg_device, args):
        """Update the current registration device."""
        try:
            if 'brand' in args:
                reg_device.brand = args.get('brand')
            if 'model_name' in args:
                reg_device.model_name = args.get('model_name')
            if 'model_num' in args:
                reg_device.model_num = args.get('model_num')
            if 'operating_system' in args:
                reg_device.operating_system = args.get('operating_system')
            if 'device_type' in args:
                device_type = DeviceType.get_device_type_id(args.get('device_type'))
                reg_device.device_types_id = device_type
            reg_device.save()
            if 'technologies' in args:
                reg_device.technologies = DeviceTechnology.update(reg_device, args.get('technologies'))
            return reg_device
        except Exception:
            raise Exception

    @classmethod
    def get_device_by_registration_id(cls, reg_id):
        """Return device by request id."""
        try:
            reg_device = cls.query.filter_by(reg_details_id=reg_id).one()
            return reg_device
        except Exception:
            return None

    @classmethod
    def get_by_id(cls, reg_device_id):
        """Return device by id."""
        return cls.query.filter_by(id=reg_device_id).first()



