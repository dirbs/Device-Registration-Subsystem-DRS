"""
DRS De-Registration Imeis Model package.
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


class DeRegImei(db.Model):
    """Database model for deregimei table."""
    __tablename__ = 'deregimei'

    id = db.Column(db.Integer, primary_key=True)
    imei = db.Column(db.String(16))
    norm_imei = db.Column(db.String(14))

    device_id = db.Column(db.Integer, db.ForeignKey('deregdevice.id', ondelete='CASCADE'))

    def __init__(self, imei, normalized_imei, de_reg_details_id):
        """Constructor."""
        self.imei = imei
        self.normalized_imei = normalized_imei
        self.de_reg_details_id = de_reg_details_id

    @classmethod
    def create_index(cls, engine):
        """ Create Indexes for De-Registration imeis table. """

        # dereg_imei = db.Index('dereg_imei_index', cls.imei)
        # dereg_imei.create(bind=engine)

        # dereg_imei_norm = db.Index('dereg_norm_imei_index', cls.norm_imei)
        # dereg_imei_norm.create(bind=engine)

    @classmethod
    def get_deregimei_list(cls, device_id, imeis):
        """Get IMEIs in list based on device id."""
        data_list = []
        if not imeis:
            return data_list
        for imei in imeis:
            data_list.append({
                "imei": imei,
                "norm_imei": imei[0:14],
                "device_id": device_id
            })
        return data_list

    @classmethod
    def get_imei(cls, imei):
        """Get an IMEI."""
        imei = DeRegImei.query.filter_by(imei=imei).first()
        return imei
