"""
DRS Utilities package.
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

import json
import os
import shutil
import threading
import time
from itertools import chain

import pydash
import requests
from flask_babel import lazy_gettext as _

from app import GLOBAL_CONF, db, app
from app.api.v1.helpers.fileprocessor import Processor
from app.api.v1.models.approvedimeis import ApprovedImeis
from app.api.v1.helpers.reports_generator import BulkCommonResources
# from app.api.v1.models.regdetails import RegDetails
# from app.api.v1.models.devicequota import DeviceQuota as DeviceQuotaModel


class Utilities:
    """Class for different util and helper functions used through out the app."""
    reg_sample_file = GLOBAL_CONF['reg_sample_file']
    dereg_sample_file = GLOBAL_CONF['dereg_sample_file']
    core_api_v1 = GLOBAL_CONF['core_api_v1']
    core_api_v2 = GLOBAL_CONF['core_api_v2']

    @staticmethod
    def remove_directory(tracking_id):
        """Method to remove/delete existing directory of a request."""
        complete_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id))
        if os.path.isdir(complete_path):
            shutil.rmtree(complete_path, ignore_errors=False, onerror=None)
        return

    @classmethod
    def get_tacs_from_devices(cls, devices):
        """Method to extract unique tacs from devices in a request."""
        tacs = []
        for device in devices:
            tac = device.get('tac')
            tacs.append(tac)
        return tacs

    @staticmethod
    def filter_imeis_by_tac(tac_imei_map, tacs):
        """Method to filter/distinguish IMEIs by unique TACs."""
        filtered_imeis = {}
        for tac in tacs:
            imeis = tac_imei_map.get(tac)
            filtered_imeis[tac] = imeis
        return filtered_imeis

    @classmethod
    def extract_imeis_tac_map(cls, args, dreg_request):
        """Method to extract and map IMEIs to TACs."""
        devices = args.get('devices')
        tacs = cls.get_tacs_from_devices(devices)
        dreg_args = {'device_count': dreg_request.device_count}
        response = cls.process_de_reg_file(dreg_request.file, dreg_request.tracking_id, dreg_args)
        imeis_tac_map = cls.filter_imeis_by_tac(response, tacs)
        return imeis_tac_map

    @classmethod
    def extract_imeis(cls, imei_tac_map):
        """Extract IMEIs from IMEI-TAC mapping."""
        imeis = []
        for tac in imei_tac_map.keys():
            tac_imeis = imei_tac_map.get(tac)
            if tac_imeis:
                imeis = imeis + tac_imeis
        return imeis

    @classmethod
    def generate_summary(cls, imeis, tracking_id):
        """Method to get compliance summary and report."""
        try:
            response = BulkCommonResources.get_summary.apply_async((imeis, tracking_id))
            # response = BulkCommonResources.get_summary(imeis, tracking_id)
            return response.id
        except Exception as e:
            app.logger.exception(e)
            return None

    @staticmethod
    def de_register_imeis(imeis):
        """Method to De-Register imeis.
        """
        # find imei devices and related imeis
        if len(imeis) == 1:
            query = """SELECT normalized_imei
                         FROM public.imeidevice
                        WHERE device_id IN
                        (SELECT device_id
                           FROM public.imeidevice
                          WHERE normalized_imei='{imei}')""".format(imei=imeis[0])
        else:
            query = """SELECT normalized_imei
                             FROM public.imeidevice
                            WHERE device_id IN 
                            (SELECT device_id
                               FROM public.imeidevice
                              WHERE normalized_imei IN {imeis})""".format(imeis=tuple(imeis))
        try:
            res = db.engine.execute(query).fetchall()
            matched_imeis = list(chain.from_iterable(res))

            # de register imeis from approved imeis
            updated_imeis = []
            for imei in matched_imeis:
                imei_ = ApprovedImeis.get_imei(imei)
                if imei_.status != 'removed':
                    imei_.status = 'removed'
                    imei_.delta_status = 'remove'
                    updated_imeis.append(imei_)
            if len(updated_imeis) > 0:
                ApprovedImeis.bulk_insert_imeis(updated_imeis)
                return True
            else:
                return False
        except Exception as e:
            app.logger.error('An exception occurred while De-Registering IMEIs see exception log:')
            app.logger.exception(e)
            return None

    @staticmethod
    def generate_imeis_file(imeis, tracking_id, file_type):
        """Method to generate a file for duplicated imeis."""
        upload_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id))
        complete_path = os.path.join(upload_path, '{0}.txt'.format(file_type))

        try:
            if not os.path.exists(os.path.dirname(complete_path)):
                os.makedirs(os.path.dirname(complete_path))
            with open(complete_path, 'w') as duplicate_imei_file:
                for imei in imeis:
                    duplicate_imei_file.write('%s\n' % imei)
            return True
        except IOError:
            app.logger.error('Could not create {0} imei file for request {1}'.format(file_type, tracking_id))
            app.logger.exception(IOError)
            return False

    @classmethod
    def pool_summary_request(cls, task_id, req, app):  # pragma: no cover
        """Method for pooling about summary request until get response back."""
        try:
            if task_id:
                req.update_report_status('Processing')
                db.session.commit()
                app.logger.info('polling task with task_id: {0} and request_id: {1}'.format(task_id, req.id))
                thread = threading.Thread(daemon=True, target=cls.check_summary_status,
                                          args=(task_id, req, app))
                thread.start()
            else:
                req.update_report_status('Failed')
                db.session.commit()
        except Exception as e:
            app.logger.exception(e)
            req.update_report_status('Failed')
            db.session.commit()

    @classmethod
    def check_summary_status(cls, task_id, req, app):  # pragma: no cover
        """Method to pool and check if the summary is available."""
        with app.app_context():
            from app import db
            try:
                task = BulkCommonResources.get_summary.AsyncResult(task_id)
                while task.state == 'PENDING':
                    task = BulkCommonResources.get_summary.AsyncResult(task_id)
                    app.logger.info('task_id:{0}-request_id:{1}-status:{2}'.
                                    format(task_id, req.id, task.state))
                task = BulkCommonResources.get_summary.AsyncResult(task_id)
                result = task.get()
                req.summary = json.dumps({'summary': result})
                req.report = result.get('compliant_report_name')

                if not app.config['AUTOMATE_IMEI_CHECK']:
                    req.update_report_status('Processed')
                    req.save()
                    db.session.commit()

                app.logger.info('task_id:{0}-request_id:{1}-status:COMPLETED'.
                                format(task_id, req.id, task.state))
            except Exception as e:
                db.session.rollback()
                if not app.config['AUTOMATE_IMEI_CHECK']:
                    req.update_report_status('Failed')
                    req.update_status('Failed')
                db.session.commit()

    @staticmethod
    def check_request_status(task_id):
        task = BulkCommonResources.get_summary.AsyncResult(task_id)

        while task.state != 'SUCCESS':
            task = BulkCommonResources.get_summary.AsyncResult(task_id)

        if task.state == 'SUCCESS':
            result = task.get()
            return result
        else:
            return False


    @classmethod
    def bulk_normalize(cls, imeis):
        """Method to transform IMEIs to normalize form in bulk."""
        norm_imeis = []
        for imei in imeis:
            norm_imei = cls.get_normalized_imei(imei)
            norm_imeis.append(norm_imei)
        return norm_imeis

    @classmethod
    def get_id_tac_map(cls, devices):
        """Method to map tacs with ids."""
        device_map_list = []
        for device in devices:
            device_map_list.append({'id': device.id, 'tac': device.tac})
        return device_map_list

    @classmethod
    def get_not_registered_imeis(cls, imeis):
        """Method to check and return IMEIs which are not already registered."""
        try:
            normalized_imeis = cls.bulk_normalize(imeis)
            query = ApprovedImeis.query.filter(ApprovedImeis.imei.in_(normalized_imeis)). \
                filter(ApprovedImeis.status == 'whitelist')
            data = query.all()
            data = list(map(lambda x: x.imei, data))
            return pydash.difference(normalized_imeis, data)
        except Exception as e:
            raise e

    @classmethod
    def get_gsma_device(cls, tacs):
        """Method to get device details from CORE GSMA TAC API."""
        tac_url = app.config['CORE_BASE_URL'] + app.config['API_VERSION'] +'/tac'
        tacs = {"tacs": tacs}
        response = requests.post(url=tac_url, json=tacs)
        return response.json()

    @classmethod
    def get_device_details_by_tac(cls, tac_imei_map):
        """Method to map device details with TACs."""

        tac_to_device_map = []
        gsma_response = cls.get_gsma_device(list(tac_imei_map.keys()))
        for response in gsma_response.get('results'):
            gsma_response = response.get('gsma')
            if gsma_response:
                model_number = gsma_response.get('internal_model_name', 'N/A')
                brand_name = gsma_response.get('brand_name', 'N/A')
                model_name = gsma_response.get('model_name', 'N/A')
                r_interface = gsma_response.get('radio_interface', 'N/A')
                if 'gsma_device_type' in gsma_response:
                    device_type = gsma_response.get('gsma_device_type', 'N/A')
                else:
                    device_type = gsma_response.get('device_type', 'N/A')
                operating_system = gsma_response.get('operating_system', 'N/A')
                count = len(tac_imei_map[response.get('tac')])
                device_info = {'tac': response.get('tac'), 'model_name': model_name, 'brand_name': brand_name,
                               'model_num': model_number, 'technology': r_interface,
                               'device_type': device_type, 'count': count, 'operating_system': operating_system}
                tac_to_device_map.append(device_info)
        return tac_to_device_map

    @staticmethod
    def update_args_with_file(files, args):
        """Method to update file args."""
        args['files'] = {}
        for file_name in files:
            file = files[file_name]
            filename = file.filename
            args['files'][file_name] = filename
        return args

    @staticmethod
    def get_normalized_imei(imei):
        """Return normalized form of an IMEI."""
        return imei[:14]

    @staticmethod
    def store_files(files, tracking_id, time):
        """Method to store files associated with a request."""
        errors = {}
        try:
            upload_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id))
            if not os.path.isdir(upload_path):
                os.mkdir(upload_path)
            for file_name in files:
                file = files[file_name]
                file_path = os.path.join(upload_path, '{0}_{1}'.format(time, file.filename))
                file.save(file_path)
                if int(Utilities.convert_to_mb(os.path.getsize(file_path))) > 26:
                    errors[file.filename] = [_('size of file is greator than 26 MB which is not allowed')]
                    os.remove(file_path)
                    break
            return errors
        except IOError:
            return IOError

    @staticmethod
    def convert_to_mb(bytes):
        """
        bytes: file bytes to convert to mb
        This method take bytes as input and
        convert it to megabytes by dividing it by 1024 twice.
        """
        floated_bytes = float(bytes)
        for i in range(2):
            floated_bytes = floated_bytes / 1024
        return floated_bytes

    @staticmethod
    def create_directory(tracking_id):
        """Create a separate directory for request."""
        upload_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id))
        if not os.path.isdir(upload_path):
            os.mkdir(upload_path)

    @staticmethod
    def store_file(file, tracking_id):
        """Method to store single file of a request."""
        errors = {}
        try:
            upload_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id))
            Utilities.create_directory(tracking_id)
            file_name = file.filename if '/' not in file.filename else file.filename.split("/")[-1]
            file_path = os.path.join(upload_path, file_name)
            file.save(file_path)
            if os.path.getsize(file_path) == 0:
                errors['size'] = ['The file should not be Empty']
            return errors
        except IOError:
            raise Exception

    @staticmethod
    def remove_file(file, tracking_id=None):
        """Method to remove file from system."""
        try:
            if not tracking_id:
                os.remove(file)
                return
            file_name = file if isinstance(file, str) else file.filename
            upload_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id))
            if os.path.isdir(upload_path):
                file_path = os.path.join(upload_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    return 'file is missing'
        except Exception as e:
            pass

    @staticmethod
    def get_files_name(files):
        """Extract file names from list of file objects."""
        names = []
        for name in files:
            filename = files[name].filename
            names.append(filename)
        return names

    @staticmethod
    def get_imei_tac(imeis):
        """Extract TAC from and IMEI."""
        return imeis[:8]

    @staticmethod
    def split_imeis(imeis):
        """Split imeis by ,"""
        if imeis:
            return imeis[1:-1].split(',')
        else:
            return None

    @staticmethod
    def process_reg_file(filename, tracking_id, args):
        """Process registration input file."""
        file_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id), filename)
        processor = Processor(file_path, args)
        response = processor.process('registration')
        return response

    @staticmethod
    def process_de_reg_file(filename, tracking_id, args):
        """Process de registration input file."""
        file_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(tracking_id), filename)
        processor = Processor(file_path, args)
        response = processor.process('de_registration')
        return response

    @staticmethod
    def exist_idx(index_name):
        """Method to check if index already exists or not."""
        query = """SELECT EXISTS(SELECT 1 
                                   FROM pg_indexes
                                  WHERE indexname = '{0}') 
                                  AS idx_exists""".format(index_name)
        res = db.engine.execute(query).first()
        return res.idx_exists

    @staticmethod
    def split_chunks(item_list, num_items_in_list):
        """Method to split lists into chunks (number of items in each list = num_items_in_list)."""
        for item in range(0, len(item_list), num_items_in_list):
            # Create an index range for item_list of num_items_in_list items:
            yield item_list[item:item + num_items_in_list]

    @staticmethod
    def get_devices_description(tacs):
        """Method to get devices description from DIRBS CORE.

        This method expect a SET of tacs.
        """
        request_url = '{base_url}{api}/tac'.format(base_url=app.config['CORE_BASE_URL'], api=app.config['API_VERSION'])
        if type(tacs) is not list:
            raise ValueError('Bad argument format for tacs')
        else:
            try:
                # if only one tac, send single tac request
                if len(tacs) == 1:
                    response = requests.get(url='{req_url}/{tac}'.format(
                        req_url=request_url, tac=tacs[0]
                    ))
                    if response.status_code == 200:
                        return json.loads(response.text)
                    return None
                elif len(tacs) <= 1000:  # if more then one tacs, send batch request
                    headers = {'content-type': 'application/json'}
                    payload = {
                        'tacs': [
                            tac for tac in tacs
                        ]
                    }
                    response = requests.post(url=request_url, data=json.dumps(payload), headers=headers)
                    if response.status_code == 200:
                        return json.loads(response.text)
                    return {}
                else:  # if tacs are more than 1000 than we have to send mutiple tac batch requests
                    # TODO: performance can be improved, use threaded approach
                    app.logger.warning('[!] Executing requests for tacs, check fo the performance stats')
                    session = requests.session()
                    tacs_list = list(Utilities.split_chunks(tacs, 1000))
                    response = []
                    headers = {'content-type': 'application/json'}
                    for tac_list in tacs_list:
                        payload = {
                            'tacs': tac_list
                        }
                        res = session.post(url=request_url, data=json.dumps(payload), headers=headers)
                        if res.status_code == 200:
                            data = json.loads(res.text)
                            response.extend(data.get('results'))
                            return response
                    return {}
            except Exception as e:
                app.logger.error('An error encountered during fetching data from DIRBS Core')
                app.logger.exception(e)
                return {}
