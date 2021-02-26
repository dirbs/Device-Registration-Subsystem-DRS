"""
DRS Registration Device Technology Model package.
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
from app import db
from app.api.v1.models.technologies import Technologies


class DeviceTechnology(db.Model):
    """Database model for devicetechnology table."""
    __tablename__ = 'devicetechnology'

    id = db.Column(db.Integer, primary_key=True)

    reg_device_id = db.Column(db.Integer, db.ForeignKey('regdevice.id', ondelete='CASCADE'))
    technology_id = db.Column(db.Integer, db.ForeignKey('technologies.id'))

    def __init__(self, reg_device_id, technology):
        """Constructor."""
        self.reg_device_id = reg_device_id
        self.technology_id = Technologies.get_technology_id(technology)

    def save(self):
        """Save the current state of the model."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def create(cls, reg_device_id, technologies, ussd_call=False):
        """Associate a technology with a request."""
        try:
            if ussd_call is False:
                for tech in technologies:
                    dev_tech = cls(reg_device_id, tech)
                    dev_tech.save()
                return technologies
            else:
                dev_tech = cls(reg_device_id, technologies)
                dev_tech.save()
                return technologies
        except Exception:
            raise Exception

    @classmethod
    def bulk_delete(cls, reg_device):
        """Delete devices technologies."""
        ids = map(lambda x: x.id, reg_device.device_technologies)
        stmt = cls.__table__.delete().where(cls.id.in_(ids))
        res = db.engine.execute(stmt)
        res.close()

    @classmethod
    def update(cls, reg_device, technologies):
        """Update a device technologies."""
        cls.bulk_delete(reg_device)
        cls.create(reg_device.id, technologies)
        return Technologies

    @classmethod
    def get_device_technologies(cls, regdevice_id):
        """Get a associated device technologies."""
        device_tech = cls.query.filter_by(reg_device_id=regdevice_id).all()
        return device_tech
