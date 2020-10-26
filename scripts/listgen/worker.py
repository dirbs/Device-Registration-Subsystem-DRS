"""
List Generator Workers Module

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
import datetime

from threading import Thread
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app import app


class IMEIWorker(Thread):
    """
    Worker for IMEI calculation for Registration Lists.
    """

    def __init__(self, in_queue, out_queue):
        """Constructor."""
        Thread.__init__(self)
        self.input_queue = in_queue
        self.output_queue = out_queue
        self.current_time_stamp = datetime.datetime.now()

    # noinspection PyMethodMayBeStatic
    def _get_details_query(self, request_id):
        """Property Method to return appropriate query for imei make, model, brand etc information."""
        return """SELECT brand, model_name, model_num, device_type, technologies
                    FROM search_registration
                   WHERE id='{0}'""".format(request_id)

    def _get_imei_details(self, imei_norm, session, list_type):
        """Property Method to return imei details."""
        imei_details = session.execute(self._get_details_query(imei_norm.request_id))
        res_dict = {}
        for row in imei_details:
            for column, value in row.items():
                res_dict.update({column: value})
        if list_type == 'delta':
            return {
                'APPROVED_IMEI': imei_norm.imei,
                'make': res_dict.get('brand'),
                'model': res_dict.get('model_name'),
                'status': imei_norm.status,
                'model_number': res_dict.get('model_num'),
                'brand_name': res_dict.get('brand'),
                'device_type': res_dict.get('device_type'),
                'radio_interface': res_dict.get('technologies', ''),
                'change_type': imei_norm.delta_status
            }
        return {
            'APPROVED_IMEI': imei_norm.imei,
            'make': res_dict.get('brand'),
            'model': res_dict.get('model_name'),
            'status': imei_norm.status,
            'model_number': res_dict.get('model_num'),
            'brand_name': res_dict.get('brand'),
            'device_type': res_dict.get('device_type'),
            'radio_interface': res_dict.get('technologies', '')
        }

    def run(self):
        """Over-ridden method to run the worker."""
        # pylint: disable=too-many-nested-blocks
        try:
            engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))
            session_factory = sessionmaker(bind=engine)
            Session = scoped_session(session_factory)
            db_session = Session()
            recs_to_export = []
            recs_to_update = []

            imei_records, list_type = self.input_queue.get()

            if list_type == 'delta':
                for imei in imei_records:
                    if imei.updated_at is not None and imei.exported_at is not None:
                        if imei.updated_at > imei.exported_at:
                            recs_to_export.append(self._get_imei_details(imei, db_session, list_type))
                            imei.exported = True
                            imei.exported_at = self.current_time_stamp
                            if imei.status == 'removed':
                                imei.removed = True
                            recs_to_update.append(imei)
                    elif imei.exported_at is None or imei.updated_at is None:
                        recs_to_export.append(self._get_imei_details(imei, db_session, list_type))
                        imei.exported = True
                        imei.exported_at = self.current_time_stamp
                        if imei.status == 'removed':
                            imei.removed = True
                        recs_to_update.append(imei)
            else:
                for imei in imei_records:
                    recs_to_export.append(self._get_imei_details(imei, db_session, list_type))
                    imei.exported = True
                    imei.exported_at = self.current_time_stamp
                    if imei.status == 'removed':
                        imei.removed = True
                    recs_to_update.append(imei)
            self.output_queue.put((recs_to_update, recs_to_export))

        finally:
            self.input_queue.task_done()
