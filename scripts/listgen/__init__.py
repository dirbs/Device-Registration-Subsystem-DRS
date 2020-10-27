"""
Registration list generator module

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
import os
import sys
import csv
import datetime

from queue import Queue
import numpy

from flask_script import Command, Option  # pylint: disable=deprecated-module

from app import app
from app.api.v1.models.approvedimeis import ApprovedImeis
from scripts.common import ScriptLogger
from scripts.listgen.worker import IMEIWorker


class ListGenerator(Command):
    """Registration List generator.

    """

    option_list = [
        Option('--list', '-l', dest='param', help='Type of list to generate (full or delta)', default='delta')
    ]

    def __init__(self, db):
        """Constructor"""
        super().__init__()
        self.db = db
        self.list_type = ''
        self.logger = ScriptLogger('list_generator').get_logger()
        self.__doc__ = self._command_description()
        self.dir_path = app.config['DRS_LISTS']
        self.current_time_stamp = datetime.datetime.now()

    # noinspection PyMethodMayBeStatic
    def _command_description(self):
        """Returns command description help."""
        return 'Command to Generate Registration List for DIRBS Core.'

    @property
    def _csv_file_name(self):
        """Property Method to return csv file name."""
        return '{0}_registration_list_{1}.csv'.format(self.list_type,
                                                      self.current_time_stamp.strftime('%Y_%m_%d_%H_%M_%S_%f'))

    def _get_details_query(self, request_id):
        """Property Method to return appropriate query for imei make, model, brand etc information."""
        return """SELECT brand, model_name, model_num, device_type, technologies
                    FROM search_registration
                   WHERE id='{0}'""".format(request_id)

    @property
    def _column_names(self):
        """Method to define column names for csv file."""
        if self.list_type == 'delta':
            return ['APPROVED_IMEI',
                    'make',
                    'model',
                    'status',
                    'model_number',
                    'brand_name',
                    'device_type',
                    'radio_interface',
                    'change_type']
        return ['APPROVED_IMEI',
                'make',
                'model',
                'status',
                'model_number',
                'brand_name',
                'device_type',
                'radio_interface']

    def generate(self, param):
        """Method to generate the list."""
        self.logger.info('checking valid directory for list generation')
        if os.path.isdir(self.dir_path):
            imeis = self.calc_imeis_to_export(param)
            if imeis:
                self.logger.info('generating {0} registration list'.format(param))
                with open('{path}/{file_name}'.format(path=self.dir_path, file_name=self._csv_file_name),
                          'w') as reglist:
                    writer = csv.DictWriter(reglist, fieldnames=self._column_names)
                    writer.writeheader()
                    writer.writerows(imeis)
                self.logger.info('{0} list [{1}] generated'.format(param, self._csv_file_name))
            else:
                self.logger.info('no imeis to export, exiting .....')
                sys.exit(0)
        else:
            self.logger.error('Error: please specify directory in config for lists')
            self.logger.info('exiting .......')
            sys.exit(0)

    def _get_imei_details(self, imei_norm):
        """Property Method to return imei details."""
        imei_details = self.db.engine.execute(self._get_details_query(imei_norm.request_id))
        res_dict = {}
        for row in imei_details:
            for column, value in row.items():
                res_dict.update({column: value})
        if self.list_type == 'delta':
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

    def calc_imeis_to_export(self, param):
        """Method to calculate imeis that needs to be exported."""
        recs_to_export = []
        recs_to_update = []

        self.logger.info('calculating imeis for {0} registration list'.format(param))
        imei_records = ApprovedImeis.imei_to_export()
        if imei_records:
            self.logger.info('{0} imei records to analyze for export'.format(len(imei_records)))
            max_workers = app.config['MAX_WORKERS']
            self.logger.info('using {0} thread workers for calculation'.format(max_workers))
            self.logger.info('spliting imeis into {0} batches'.format(max_workers))
            imei_records = numpy.array_split(imei_records, max_workers)
            self.logger.info('splited imeis into {0} batches'.format(len(imei_records)))

            input_queue = Queue()
            output_queue = Queue()

            for worker in range(max_workers):  # pylint: disable=unused-variable
                imei_worker = IMEIWorker(in_queue=input_queue, out_queue=output_queue)
                imei_worker.daemon = True
                imei_worker.start()

            for imei_record in imei_records:
                input_queue.put((imei_record, param))

            input_queue.join()
            for i in range(max_workers):  # pylint: disable=unused-variable
                rec_update, rec_export = output_queue.get()
                if rec_update:
                    recs_to_update.extend(rec_update)
                if rec_export:
                    recs_to_export.extend(rec_export)
            ApprovedImeis.bulk_insert_imeis(recs_to_update)
            return recs_to_export
        else:
            self.logger.info('no records founds to export, exiting...')
            sys.exit(0)

    # noinspection PyMethodOverriding
    def run(self, param):  # pylint: disable=method-hidden,arguments-differ,
        """Overloaded method of the super class."""
        if param in ['delta', 'full']:
            self.list_type = param
            self.generate(param)
            return 'List generation successful'
        else:
            return 'Wrong command line argument, available options are: full, delta'
