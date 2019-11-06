import os
import sys

import pandas as pd
from datetime import datetime

from app import app
from app.api.v1.models.association import ImeiAssociation
from scripts.common import ScriptLogger


class Helper:

    def __init__(self):
        """Constructor"""
        self.dir_path = app.config['DDCDS_LISTS']
        self.current_time_stamp = datetime.now().strftime("%m-%d-%YT%H%M%S")
        self.logger = ScriptLogger('list_generator').get_logger()

    @staticmethod
    def get_imeis():
        case_list = []
        for row in ImeiAssociation.get_all_imeis():
            case_list.append(dict((col, val) for col, val in row.items()))
        return case_list

    @staticmethod
    def add_to_list(full_list, imei, status):
        full_list.append({"imei": imei['imei'], "reported_date": imei['start_date'], "status": status})
        return full_list

    def upload_list(self, list, name):
        try:
            if os.path.isdir(self.dir_path):
                full_list = pd.DataFrame(list)
                report_name = name + self.current_time_stamp + '.csv'
                full_list.to_csv(os.path.join(self.dir_path, report_name), sep=',', index=False)
                self.logger.info("Full list saved successfully")
                return "List " + report_name + " has been saved successfully."
            else:
                self.logger.error('Error: please specify directory in config for lists')
                self.logger.info('exiting .......')
                sys.exit(0)
        except Exception as e:
            self.logger.critical("Exception occurred while uploading delta list")
            self.logger.exception(e)
            self.logger.exception("Exception occurred while uploading list.")