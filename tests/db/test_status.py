"""
Status Model Unittests

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
from app.api.v1.models.status import Status


def test_get_status_id(session):
    """Verify that the get_status_id() returns correct
    status id provided the description.
    """
    # create an entry in table
    statuses = [
        Status(id=111, description='ABCD'),
        Status(id=112, description='BCDE'),
        Status(id=133, description='GHIJK')
    ]
    session.bulk_save_objects(statuses)
    session.commit()
    assert Status.get_status_id('ABCD') == 111
    assert Status.get_status_id('BCDE') == 112
    assert Status.get_status_id('GHIJK') == 133
    assert Status.get_status_id('test') is None


def test_get_status_type(session):
    """Verify that the get_status_type returns
    correct status description provided the status id.
    """
    # create an entry in table
    statuses = [
        Status(id=115, description='ABCD'),
        Status(id=116, description='BCDE'),
        Status(id=122, description='GHIJK')
    ]
    session.bulk_save_objects(statuses)
    session.commit()
    assert Status.get_status_type(115) == 'ABCD'
    assert Status.get_status_type(116) == 'BCDE'
    assert Status.get_status_type(122) == 'GHIJK'
    assert Status.get_status_type(32424453453) is None


def test_get_status_types(session):
    """Verify that the status_types() returns all the statuses in the table."""
    statuses = [
        Status(id=344, description='ABCD'),
        Status(id=888, description='BCDE'),
        Status(id=999, description='GHIJK')
    ]
    session.bulk_save_objects(statuses)
    session.commit()
    res = Status.get_status_types()
    assert res
