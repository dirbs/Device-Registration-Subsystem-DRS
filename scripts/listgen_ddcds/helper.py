import os
import sys

import pandas as pd
from datetime import datetime
from collections import OrderedDict

from app import app
from app.api.v1.models.association import ImeiAssociation


class Helper:

    def __init__(self, logger):
        """Constructor"""
        self.dir_path = app.config['DDCDS_LISTS']
        self.current_time_stamp = datetime.now().strftime("%m-%d-%YT%H%M%S")
        self.logger = logger

    def get_imeis(self):
        try:
            case_list = []
            self.logger.info("Extracting IMEIs to export...")
            for row in ImeiAssociation.get_all_imeis():
                case_list.append(dict((col, val) for col, val in row.items()))
            return case_list
        except Exception as e:
            self.logger.critical("Exception occurred while extracting IMEIs from db.")
            self.logger.exception(e)

    def add_to_delta_list(self, full_list, imei, status):
        try:
            delta_dict = OrderedDict()
            delta_dict['uid'] = imei['uid']
            delta_dict['imei'] = imei['imei']
            delta_dict['change_type'] = status
            full_list.append(delta_dict)
            return full_list
        except Exception as e:
            self.logger.critical("Exception occurred while adding IMEIs to list.")
            self.logger.exception(e)

    def add_to_full_list(self, full_list, imei):
        try:
            full_dict = OrderedDict()
            full_dict['uid'] = imei['uid']
            full_dict['imei'] = imei['imei']
            full_list.append(full_dict)
            return full_list
        except Exception as e:
            self.logger.critical("Exception occurred while adding IMEIs to list.")
            self.logger.exception(e)


    def upload_list(self, list, name):
        try:
            self.logger.info("Checking if list directory exists...")
            if os.path.isdir(self.dir_path):
                full_list = pd.DataFrame(list)
                report_name = name + self.current_time_stamp + '.csv'
                self.logger.info("Saving list to specified directory...")
                full_list.to_csv(os.path.join(self.dir_path, report_name), sep=',', index=False)
                self.logger.info("List " + report_name + " has been saved successfully.")
                sys.exit(0)
            else:
                self.logger.error('Error: please specify directory in config for lists')
                self.logger.info('exiting .......')
                sys.exit(0)
        except Exception as e:
            self.logger.critical("Exception occurred while uploading delta list")
            self.logger.exception(e)
            self.logger.exception("Exception occurred while uploading list.")