"""
DRS Registration Comments Model package.
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
from sqlalchemy import desc

from app import db


class RegComments(db.Model):
    """Database model for regcomments table."""
    __tablename__ = 'regcomments'

    id = db.Column(db.Integer, primary_key=True)
    step = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String(64), nullable=False)
    user_name = db.Column(db.String(64), nullable=False)
    added_at = db.Column(db.DateTime, server_default=db.func.now())

    status = db.Column(db.Integer, db.ForeignKey('status.id'))
    reg_details_id = db.Column(db.Integer, db.ForeignKey('regdetails.id', ondelete='CASCADE'))

    def __init__(self, section, comment, user_id, user_name, status, request_id):
        """Constructor"""
        self.step = section
        self.comment = comment
        self.user_id = user_id
        self.user_name = user_name
        self.status = status
        self.reg_details_id = request_id

    @classmethod
    def add(cls, section, comment, user_id, user_name, status, request_id):
        """Method to add comment"""
        comment = cls(section, comment, user_id, user_name, status, request_id)
        try:
            db.session.add(comment)
        except Exception:
            db.session.rollback()
            raise Exception

    @staticmethod
    def get_all_by_regid(request_id):
        """Method to get all comments and sections by request id.

        Returns results order by added_at descending.
        """
        return RegComments.query\
            .order_by(desc(RegComments.added_at))\
            .filter_by(reg_details_id=request_id).all()

    @staticmethod
    def get_all_by_section_type(request_id, section_type):
        """Method to get section data by section type."""
        return RegComments.query.order_by(desc(RegComments.added_at))\
            .filter_by(reg_details_id=request_id).filter_by(step=section_type).all()
