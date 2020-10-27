"""
DRS Registration Imei Device Model package.
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
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.helpers.utilities import Utilities


class ImeiDevice(db.Model):
    """Database model for imeidevice table."""
    __tablename__ = 'imeidevice'

    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(16))
    normalized_imei = db.Column(db.String(14))
    device_id = db.Column(db.Integer, db.ForeignKey('device.id', ondelete='CASCADE'))

    def __init__(self, imei, device_id):
        """Constructor."""
        self.imei = imei
        self.normalized_imei = imei[:14]
        self.device_id = device_id

    @classmethod
    def create_index(cls, engine):
        """ Create Indexes for Registration imeidevice table. """

        reg_imei = db.Index('reg_imei_index', cls.imei, postgresql_concurrently=True)
        reg_imei.create(bind=engine)

        reg_normalized_imei = db.Index('reg_normalized_imei_index', cls.normalized_imei, postgresql_concurrently=True)
        reg_normalized_imei.create(bind=engine)

    @classmethod
    def create(cls, imei, device_id):
        """Create an imei device."""
        try:
            imei_device = cls(imei, device_id)
            imei_device.save()
        except Exception:
            raise Exception

    def save(self):
        """Save current state of the model."""
        try:
            db.session.add(self)
            db.session.flush()
        except Exception:
            db.session.rollback()
            raise Exception

    @staticmethod
    def get_imei_device(imei):
        """Method to return a device id of an imei."""
        return ImeiDevice.query.filter_by(imei=imei).first()

    @classmethod
    def bulk_insert(cls, device_id, imeis):
        """Insert imeis in bulk."""
        insertion_object = []
        for imei in imeis:
            insertion_object.append({'imei': imei, 'normalized_imei':  imei[0:14], 'device_id': device_id})
        res = db.engine.execute(ImeiDevice.__table__.insert(), insertion_object)
        res.close()

