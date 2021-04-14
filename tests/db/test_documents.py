"""
Documents Model Unittests

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
from app.api.v1.models.documents import Documents


def test_get_label_by_id(session):
    """Verify that the get_label_by_id() returns correct document label when id is provided."""
    docs = [
        Documents(id=111, label='shp doc', type=1, required=True),
        Documents(id=211, label='ath doc', type=1, required=True)
    ]
    session.bulk_save_objects(docs)
    session.commit()
    assert Documents.get_label_by_id(111) == 'shp doc'
    assert Documents.get_label_by_id(211) == 'ath doc'
    assert Documents.get_label_by_id(2334242323322) is None


def test_get_document_by_id(session):
    """Verify that the get_document_by_id returns a document provided an id."""
    docs = [
        Documents(id=1110, label='shp doc', type=1, required=True),
        Documents(id=2110, label='ath doc', type=1, required=True)
    ]
    session.bulk_save_objects(docs)
    session.commit()
    assert Documents.get_document_by_id(1110)
    assert Documents.get_document_by_id(2110)
    assert Documents.get_document_by_id(79897777879) is None


def test_get_document_by_name(session):
    """Verify that the get_document_by_name() returns a document provided the name."""
    docs = [
        Documents(id=11101, label='shp doc', type=1, required=True),
        Documents(id=21102, label='ath doc', type=2, required=True)
    ]
    session.bulk_save_objects(docs)
    session.commit()
    assert Documents.get_document_by_name('shp doc', 1)
    assert Documents.get_document_by_name('ath doc', 2)
    assert Documents.get_document_by_name('88668', 1) is None


def test_get_documents(session):
    """Verify that the get_documents() returns all the documents of same type."""
    docs = [
        Documents(id=11101003, label='shp doc', type=1, required=True),
        Documents(id=21102004, label='ath doc', type=1, required=True),
        Documents(id=11101005, label='shp doc', type=2, required=True),
        Documents(id=21102006, label='ath doc', type=2, required=True)
    ]
    session.bulk_save_objects(docs)
    session.commit()
    docs_1 = Documents.get_documents('registration')
    assert docs_1
    for doc in docs_1:
        assert doc.type == 1

    docs_2 = Documents.get_documents('avddd')
    assert docs_1
    for doc in docs_2:
        assert doc.type == 2


def test_required_docs(session):
    """Verify that the required_docs() only returns docs for which the required flag is true."""
    docs = [
        Documents(id=111010034, label='shp doc', type=1, required=True),
        Documents(id=211020045, label='ath doc', type=1, required=False),
        Documents(id=111010056, label='shp doc', type=2, required=True),
        Documents(id=211020067, label='ath doc', type=2, required=True)
    ]
    session.bulk_save_objects(docs)
    session.commit()
    docs = Documents.get_required_docs('registration')
    for doc in docs:
        assert doc.required
    docs = Documents.get_required_docs('avdd')
    for doc in docs:
        assert doc.required
