"""
DRS Approved Imeis Unit tests.
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
from sqlalchemy import text

from app.api.v1.models.approvedimeis import ApprovedImeis


def test_add(db, session):  # pylint: disable=unused-argument
    """Verify that the approved imeis add function works correctly."""
    # add data using model's add function
    imei_norm = '12345678901234'
    request_id = 2376322
    status = 'status'
    delta_status = 'delta status'
    approved_imei = ApprovedImeis(imei_norm, request_id, status, delta_status)
    approved_imei.add()

    # extract data and verify
    imei_data = session.execute(text("""SELECT *
                                          FROM public.approvedimeis 
                                         WHERE imei='{0}'""".format(imei_norm))).fetchone()
    assert imei_data
    assert imei_data.imei == imei_norm
    assert imei_data.request_id == request_id
    assert imei_data.status == status
    assert imei_data.delta_status == delta_status

    # check some default params
    assert not imei_data.exported  # exported should be false as default
    assert imei_data.exported_at is None  # when not exported than exported_at should be none
    assert not imei_data.removed  # removed should be false as default

    # verify that exported and removed params can be altered by add function
    imei_norm = '23456789064573'
    request_id = 23765466
    status = 'status'
    delta_status = 'delta status'
    approved_imei = ApprovedImeis(imei_norm, request_id, status, delta_status, True, True)
    approved_imei.add()

    imei_data = session.execute(text("""SELECT *
                                              FROM public.approvedimeis 
                                             WHERE imei='{0}'""".format(imei_norm))).fetchone()
    assert imei_data.exported
    assert imei_data.removed


def test_get_imei(db, session):  # pylint: disable=unused-argument
    """Verify that the get_imei() return the same imei which is not removed."""
    imei_norm = '23456421264573'
    request_id = 237654998
    status = 'status'
    delta_status = 'delta status'
    approved_imei = ApprovedImeis(imei_norm, request_id, status, delta_status)
    approved_imei.add()

    # get imei
    imei_data = ApprovedImeis.get_imei(imei_norm)
    assert imei_data.imei == imei_norm
    assert imei_data.request_id == request_id
    assert imei_data.status == status
    assert imei_data.delta_status == delta_status
    assert not imei_data.removed

    # update removed=True and check again
    res = session.execute(text("""UPDATE public.approvedimeis
                                    SET removed=True
                                   WHERE imei='{0}' AND request_id='{1}'""".format(imei_norm, request_id)))
    assert res
    imei_data = ApprovedImeis.get_imei(imei_norm)
    assert not imei_data


def test_exists(db, session):  # pylint: disable=unused-argument
    """Verify that the exists function works correctly."""
    # if there is no imei in the table
    imei_norm = '64728204390652'
    model_exists = ApprovedImeis.exists(imei_norm)
    query_exists = session.execute(text("""SELECT EXISTS(
                                             SELECT 1 FROM public.approvedimeis
                                            WHERE imei='{0}' AND removed IS NOT TRUE )""".format(imei_norm))).fetchone()
    assert query_exists[0] == model_exists

    # add a record and than check
    imei_norm = '64728204390652'
    request_id = 237654998
    status = 'status'
    delta_status = 'delta status'
    approved_imei = ApprovedImeis(imei_norm, request_id, status, delta_status)
    approved_imei.add()
    assert ApprovedImeis.exists(imei_norm)

    # set existing record's removed=True than check
    res = session.execute(text("""UPDATE public.approvedimeis
                                        SET removed=True
                                       WHERE imei='{0}' 
                                       AND request_id='{1}'""".format(imei_norm, request_id)))
    assert res
    assert not ApprovedImeis.exists(imei_norm)


def test_bulk_insert_imeis(db, session):  # pylint: disable=unused-argument
    """Verify that the bulk_insert_imeis() works as expected."""
    imei_norm1 = '67895678901234'
    imei_norm2 = '76545678906548'
    imei_norm3 = '54375699900000'
    request_id = 2376322
    status = 'status'
    delta_status = 'delta status'
    imeis = [
        ApprovedImeis(imei_norm1, request_id, status, delta_status),
        ApprovedImeis(imei_norm2, request_id, status, delta_status),
        ApprovedImeis(imei_norm3, request_id, status, delta_status)
    ]
    ApprovedImeis.bulk_insert_imeis(imeis)
    assert ApprovedImeis.exists(imei_norm1)
    assert ApprovedImeis.exists(imei_norm2)
    assert ApprovedImeis.exists(imei_norm3)


def test_imeis_to_export(db, session):  # pylint: disable=unused-argument
    """Verify that imeis_to_export() works as expected."""
    imei_norm1 = '67890000001234'
    imei_norm2 = '71111178906548'
    imei_norm3 = '54322333900000'
    request_id = 2376322
    status = 'status'
    delta_status = 'delta status'
    imeis = [
        ApprovedImeis(imei_norm1, request_id, status, delta_status),
        ApprovedImeis(imei_norm2, request_id, status, delta_status),
        ApprovedImeis(imei_norm3, request_id, status, delta_status)
    ]
    ApprovedImeis.bulk_insert_imeis(imeis)
    imeis_to_export = ApprovedImeis.imei_to_export()
    assert imeis_to_export
    for imei in imeis_to_export:
        assert imei.removed is False
