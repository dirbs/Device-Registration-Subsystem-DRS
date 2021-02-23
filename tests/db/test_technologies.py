"""
Technologies Model Unittests

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
from app.api.v1.models.technologies import Technologies


def test_get_technology_id(session):
    """Verify that the get_technology_id() returns
    correct id of the technology in the table provided
    technology type.
    """
    # insert data
    techs = [
        Technologies(id=123, description='123 Tech'),
        Technologies(id=567, description='567 Tech'),
        Technologies(id=890, description='890 Tech')
    ]
    session.bulk_save_objects(techs)
    session.commit()
    assert Technologies.get_technology_id('123 Tech') == 123
    assert Technologies.get_technology_id('567 Tech') == 567
    assert Technologies.get_technology_id('890 Tech') == 890
    assert Technologies.get_technology_id('hdheukkslkl') is None


def test_get_technologies(session):
    """Verify that the get_technologies returns all the technologies in the database."""
    techs = [
        Technologies(id=1231, description='123 Tech'),
        Technologies(id=5671, description='567 Tech'),
        Technologies(id=8901, description='890 Tech')
    ]
    session.bulk_save_objects(techs)
    session.commit()
    assert Technologies.get_technologies()


def test_get_technologies_names(session):
    """Verify that the get_technologies_names() return names of all technologies."""
    techs = [
        Technologies(id=12312, description='123 Tech'),
        Technologies(id=56712, description='567 Tech'),
        Technologies(id=89012, description='890 Tech')
    ]
    session.bulk_save_objects(techs)
    session.commit()
    for name in Technologies.get_technologies_names():
        assert isinstance(name, str)


def test_get_technology_by_id(session):
    """Verify that the get_technology_by_id() returns description provided the id is given."""
    techs = [
        Technologies(id=123123, description='123 Tech'),
        Technologies(id=567123, description='567 Tech'),
        Technologies(id=890123, description='890 Tech')
    ]
    session.bulk_save_objects(techs)
    session.commit()
    assert Technologies.get_technology_by_id(123123) == '123 Tech'
    assert Technologies.get_technology_by_id(567123) == '567 Tech'
    assert Technologies.get_technology_by_id(890123) == '890 Tech'
    assert Technologies.get_technology_by_id(283802818388) is None
