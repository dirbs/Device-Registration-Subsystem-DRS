"""
DRS Registration Device Quota Model package.
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
from app import GLOBAL_CONF
from app import db
from app.api.v1.schema.devicequota import DeviceQuotaSchema


class DeviceQuota(db.Model):
    """Database model for devicequota table."""
    __tablename__ = 'devicequota'

    USER_TYPE_MAP = {'individual': 1, 'exporter': 2, 'importer': 3, 'ussd': 4}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=False)
    user_type = db.Column(db.Integer)
    reg_quota = db.Column(db.Integer)
    dreg_quota = db.Column(db.Integer)

    def __init__(self, user_id, user_type):
        """Constructor."""
        self.user_id = user_id
        self.user_type = DeviceQuota.USER_TYPE_MAP.get(user_type)
        self.reg_quota = DeviceQuota.get_reg_quota()
        self.dreg_quota = DeviceQuota.get_dreg_quota()

    @classmethod
    # @lru_cache()
    def get_reg_quota(cls):
        """Get registration quota of importer."""
        return int(GLOBAL_CONF['importer'])

    @classmethod
    def update_reg_quota(cls, user_id, device_count):
        """Update remaining registration quota of importer."""
        device_quota = cls.get(user_id)
        if device_quota and device_quota.reg_quota >= device_count:
            quota_left = device_quota.reg_quota - device_count
            device_quota.reg_quota = quota_left
        device_quota.save()

    @classmethod
    # @lru_cache()
    def get_dreg_quota(cls):
        """Get remaining de registration quota of an exporter."""
        return GLOBAL_CONF['exporter']

    @classmethod
    def get_or_create(cls, user_id, user_type):
        """Create quota for a user."""
        schema = DeviceQuotaSchema()
        quota = cls.get(user_id)
        if not quota:
            quota = cls.create(user_id, user_type)
        return schema.dump(quota).data

    @staticmethod
    def commit_quota_changes(device_quota):
        """Method to commit changes to the quota."""
        try:
            db.session.add(device_quota)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    # @lru_cache()
    def get(cls, user_id):
        """Get remaining quota of a user."""
        quota = cls.query.filter_by(user_id=user_id).first()
        return quota

    @classmethod
    def create(cls, user_id, user_type):
        """Create quota for a user."""
        quota = DeviceQuota(user_id, user_type)
        quota.save()
        return quota

    def save(self):
        """Save the current state of the model."""
        try:
            db.session.add(self)
            db.session.flush()
        except Exception:
            db.session.rollback()
            raise Exception
