"""
DRS Registration Document Model package.
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
from app.api.v1.helpers.utilities import Utilities
from app.api.v1.models.documents import Documents


class RegDocuments(db.Model):
    """Database model for regdocuments table."""
    __tablename__ = 'regdocuments'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))

    reg_details_id = db.Column(db.Integer, db.ForeignKey('regdetails.id', ondelete='CASCADE'))
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id', ondelete='CASCADE'))

    def __init__(self, filename):
        """Constructor."""
        self.filename = filename

    @staticmethod
    def get_document(reg_details_id, filename):
        """Return documents of the current request."""
        return RegDocuments.query.filter_by(reg_details_id=reg_details_id, filename=filename).first()

    @classmethod
    def bulk_create(cls, documents, reg_details, time):
        """Create documents for a request in bulk."""
        try:
            created_documents = []
            for name in documents:
                document = Documents.get_document_by_name(name, 1)
                reg_document = cls(filename='{0}_{1}'.format(time, documents[name].filename))
                reg_document.reg_details_id = reg_details.id
                reg_document.document_id = document.id
                reg_document.save()
                created_documents.append(reg_document)
            return created_documents
        except Exception:
            raise Exception

    @classmethod
    def bulk_update(cls, documents, reg_details, time):
        """Update documents of a request in bulk."""
        try:
            updated_documents = []
            for name in documents:
                document = Documents.get_document_by_name(name, 1)
                cls.trash_document(document.id, reg_details)
                reg_document = cls(filename='{0}_{1}'.format(time, documents[name].filename))
                reg_document.reg_details_id = reg_details.id
                reg_document.document_id = document.id
                reg_document.save()
                updated_documents.append(reg_document)
            return updated_documents
        except Exception:
            raise Exception

    @classmethod
    def trash_document(cls, type_id, reg_details):
        """Purge documents of a request."""
        try:
            document = cls.query.filter_by(document_id=type_id, reg_details_id=reg_details.id).one()
            cls.delete(document.id)
            Utilities.remove_file(document.filename, reg_details.tracking_id)
        except Exception:
            raise Exception

    @classmethod
    def delete(cls, document_id):
        """Delete a document."""
        try:
            cls.query.filter_by(id=document_id).delete()
        except Exception:
            raise Exception

    @classmethod
    def get_by_reg_id(cls, reg_id):
        """Return a document by request id."""
        documents = cls.query.filter_by(reg_details_id=reg_id).all()
        return documents

    @classmethod
    def get_by_id(cls, doc_id):
        """Return a document by id."""
        documents = cls.query.filter_by(id=doc_id).one()
        return documents

    def save(self):
        """Save the current state of the model."""
        try:
            db.session.add(self)
            db.session.flush()
        except Exception:
            db.session.rollback()
            raise Exception
