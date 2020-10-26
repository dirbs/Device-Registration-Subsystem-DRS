"""
DRS Registration Documents Model package.
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
from functools import lru_cache


class Documents(db.Model):
    """Database model for supported documents table."""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False)
    type = db.Column(db.SmallInteger, nullable=False)
    required = db.Column(db.Boolean, nullable=False)

    @staticmethod
    @lru_cache(maxsize=32)
    def get_label_by_id(document_id):
        """Return document label by id."""
        document = Documents.query.filter_by(id=document_id).first()
        if document:
            return document.label
        return document

    @staticmethod
    def get_document_by_id(document_id):
        """Return a document object by id."""
        return Documents.query.filter_by(id=document_id).first()

    @staticmethod
    def get_document_by_name(label, doc_type):
        """Return a document by name."""
        return Documents.query.filter_by(type=doc_type, label=label).first()

    @staticmethod
    @lru_cache(maxsize=32)
    def get_documents(doc_type):
        """Return documents by request type."""
        doc_type = 1 if doc_type == 'registration' else 2
        return Documents.query.filter_by(type=doc_type).all()

    @staticmethod
    # @lru_cache(maxsize=32)
    def get_required_docs(doc_type):
        """Return list of required documents by document type."""
        doc_type = 1 if doc_type == 'registration' else 2
        return Documents.query.filter_by(type=doc_type, required=True).all()
