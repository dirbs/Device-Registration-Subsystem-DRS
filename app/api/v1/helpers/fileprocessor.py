"""
DRS File Processor package.
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
import pandas as pd
from pandas import Series
import numpy as np
from marshmallow import ValidationError
from flask_babel import lazy_gettext as _
from app import db, app


class Processor:
    """Class for processing input files for Device Registration."""

    def __init__(self, file_path, args, parent_reg_details=None):
        """Constructor."""
        self.file_path = file_path
        self.device_count = int(args.get('device_count'))
        self.data = Processor.extract_data(file_path)
        self.series_data = self.transform_to_series()
        self.imei_per_device = int(args.get('imei_per_device')) if 'imei_per_device' in args else \
            int(Processor.extract_imei_per_device(self.data))
        self.args = args
        self.parent_reg_details = parent_reg_details

    @staticmethod
    def extract_imei_per_device(data):
        """Method to extract IMEIs per device from file object."""
        return len(data.columns)

    @classmethod
    def read_txt_file(cls, file_path):
        """Method to read and load text file into data frame."""
        data = pd.read_csv(file_path, skip_blank_lines=True, dtype=str, header=None).dropna(axis=1, how='all')
        data = pd.DataFrame(data)
        return data

    @classmethod
    def read_tsv_file(cls, file_path):
        """Method to read and load TSV file into data frame."""
        data = pd.read_csv(file_path, skip_blank_lines=True, error_bad_lines=False, warn_bad_lines=True, dtype=str,
                           delim_whitespace=True, header=None).dropna(axis=1, how='all')
        data = pd.DataFrame(data)
        return data

    @classmethod
    def extract_data(cls, file_path):
        """Method to read and return the correct file type."""
        if file_path.endswith('.txt'):
            return cls.read_txt_file(file_path)
        else:
            return cls.read_tsv_file(file_path)

    def validate_imei_per_device(self):
        """Method to validate if IMEI per device count is matched to the IMEIs in file."""
        if len(self.data.columns) == self.imei_per_device:
            return True
        else:
            return False

    def validate_device_count(self):
        """Method to validate if Device count is matched to devices in file."""
        if len(self.data.index) == self.device_count:
            return True
        else:
            return False

    def check_rows_limit(self):
        """Method to check the rows limit in data frame."""
        if len(self.data.index) > 10000000:
            return False
        else:
            return True

    def validate_missing_imei(self):
        """Method to validate missing IMEIs in file."""
        if self.data.isnull().any(axis=1).sum() > 0:
            return True
        else:
            return False

    def find_null_locations(self):
        """Method to validate and find null locations in file."""
        null_values = (data.loc[(self.data['null values'] == 1)].drop(columns=['null values']))
        return null_values

    def transform_to_series(self):
        """Method to transform file data to pandas series."""
        series_data = pd.Series(self.data.values.ravel('F')).dropna()
        series_data = pd.DataFrame(series_data)
        series_data = series_data.rename(columns={0: "IMEIs"}).dropna()
        return series_data

    def get_invalid_imeis(self):
        """Method to find invalid IMEIs in file data."""
        self.series_data['length'] = self.series_data['IMEIs'].str.len()
        self.series_data['valid'] = (self.series_data['length'] >= 14) & (self.series_data['length'] <= 16)
        series_data = self.series_data.loc[(self.series_data['valid']==False)].drop(columns=['valid', 'length'])
        series_data = series_data.to_dict(orient='list')
        return series_data["IMEIs"]

    def check_imei_format(self):
        """Method to validate IMEI format."""
        self.series_data['alpha_num'] = self.series_data['IMEIs'].str.isdigit()
        return self.series_data.loc[(self.series_data['alpha_num']==False)]

    def match_imei_records(self, record):
        """Method to validate IMEIs between parts applications."""

        current_file_data = self.series_data

        record_file_path = os.path.join(app.config['DRS_UPLOADS'], '{0}'.format(record[12]), record[9])

        record_file_data = self.read_tsv_file(record_file_path)

        series_data = pd.Series(record_file_data.values.ravel('F')).dropna()
        series_data = pd.DataFrame(series_data)
        series_data = series_data.rename(columns={0: "IMEIs"}).dropna()

        series_data_sorted = series_data.sort_values("IMEIs")

        series_data_sorted_indexed = series_data_sorted.reset_index(drop=True)

        series_data_sorted_indexed_dataframe = series_data_sorted_indexed.values[:, 0]

        current_file_data_sorted = current_file_data.sort_values("IMEIs")
        current_file_data_sorted_indexed = current_file_data_sorted['IMEIs'].reset_index(drop=True)

        comparison_column = np.where(series_data_sorted_indexed_dataframe == current_file_data_sorted_indexed, True, False)

        if np.all(comparison_column):
            return True
        else:
            return False


    def check_for_same_imeis_applied(self):
        """Method to validate Count, number of IMEIs per device and IMEIs in file for redundant application in parts."""
        # check for devices with same device_count and number_of_IMEIs per device
        query = """SELECT * FROM public.regdetails WHERE m_location='local' AND device_count='{device_count}' 
                    AND imei_per_device='{imei_per_device}' AND processing_status='10'
                    """.format(device_count=self.args.get("device_count"), imei_per_device=self.args.get("imei_per_device"))
        try:
            parts_applications_res = db.engine.execute(query).fetchall()
            for single_record in parts_applications_res:
                # check current record IMEIs with records in DB
                if self.match_imei_records(single_record):
                    return True
            return False

        except Exception as e:
            app.logger.error('An exception occurred while De-Registering IMEIs see exception log:')
            app.logger.exception(e)
            return None


    def get_duplicate_imeis(self):
        """Method to find duplicate IMEIs in file."""
        self.series_data['Duplication'] = self.series_data.duplicated(keep='first')
        duplication = self.series_data.loc[(self.series_data['Duplication'] == True)]\
            .drop(columns=['Duplication', 'length', 'valid'])
        return duplication.to_dict(orient='list')

    def get_unique_tags(self):
        """Method to extract unique TACs from file."""
        self.series_data['Tacs'] = self.series_data['IMEIs'].str[0:8].astype(str)
        unique_tacs = self.series_data['IMEIs Tac'].unique()
        return unique_tacs

    def transform_dreg_data(self):
        """Method to transform data to dictionaries."""
        response_dict = {}
        data = self.data.rename(columns={0: "IMEIs"}).dropna()
        data['IMEIs Tac'] = data['IMEIs'].str[0:8].astype(str)
        for i in data['IMEIs Tac'].unique():
            response_dict[i] = [data['IMEIs'][j] for j in data[data['IMEIs Tac'] == i].index]
        return response_dict

    def transform_data(self, type):
        """Method to return transformed data."""
        if type == 'registration':
            return self.data.values.tolist()
        elif type == 'assembled_registration':
            return np.hstack(self.data.values)
        else:
            return self.transform_dreg_data()

    def validate_registration(self):
        """Method to validate registration request data."""
        errors = {}
        invalid_imeis = self.get_invalid_imeis()
        duplicate_imeis = self.get_duplicate_imeis()
        missing_imeis = self.validate_missing_imei()
        rows_limit = self.check_rows_limit()
        invalid_format = self.check_imei_format()

        # if local, then validate for same application already approved
        if self.args.get("m_location"):
            already_applied = self.check_for_same_imeis_applied()
        else:
            already_applied = False
        # If user needs the list of imeis on the frontend we can show it.
        if not self.validate_imei_per_device():
            errors['imei_per_device'] = [_("IMEIs per device count in file is not same as input.")]
        if not self.validate_device_count():
            errors['device_count'] = [_("Device count in file is not same as input")]
        if len(invalid_imeis) > 0:
            errors['invalid_imeis'] = [_("Invalid IMEIs in the input file")]
        if len(duplicate_imeis['IMEIs']) > 0:
            errors['duplicate_imeis'] = [_("Duplicate IMEIs in the input file")]
        if missing_imeis:
            errors['missing_imeis'] = [_("Some IMEIs are missing in the columns")]
        if not rows_limit:
            errors['limit'] = [_("Rows limit is 10000000 for single request")]
        if len(invalid_format) > 0:
            errors['invalid_format'] = [_("Invalid IMEIs Format in input file")]
        if already_applied:
            errors['already_applied'] = [_("Another application for parts with the same number of IMEIs, device count and IMEIs also exists for assembly.")]
        return errors

    def check_parent_child_mismatch(self):
        """Method to find parent child IMEIs mismatch in file."""
        # print("Printing the parent file things")
        child_file_imeis = self.data
        parent_file_imeis = self.read_tsv_file(self.parent_reg_details.parent_file_path)

        df_row_reindex = pd.concat([parent_file_imeis, child_file_imeis], ignore_index=True)
        resultant_imei_file_after_filter = df_row_reindex.drop_duplicates()

        try:
            resultant_df = parent_file_imeis.compare(resultant_imei_file_after_filter)
            if resultant_df.empty:
                # exactly matched with the parent file after filtering
                return False
            else:
                return True
        except Exception as e:  # pragma: no cover
            print(e)
            return True

    def check_parent_child_id_mismatch(self):
        """Method to find parts and assembled authorized user_id."""
        try:
            if self.parent_reg_details.user_id == self.args.get("user_id"):
                return False
            else:
                return True
        except Exception as e:  # pragma: no cover
            print(e)
            return True

    def check_parent_approved(self):
        """Method to find parts and assembled authorized user_id."""
        try:
            if self.parent_reg_details.processing_status == 10 and self.parent_reg_details.report_status == 10:
                return False
            else:
                return True
        except Exception as e:  # pragma: no cover
            print(e)
            return True


    def validate_assembled_registration(self):
        """Method to validate registration request data."""
        errors = {}
        invalid_imeis = self.get_invalid_imeis()
        duplicate_imeis = self.get_duplicate_imeis()
        missing_imeis = self.validate_missing_imei()
        rows_limit = self.check_rows_limit()
        invalid_format = self.check_imei_format()
        parent_child_mismatch = self.check_parent_child_mismatch()
        parent_child_id_mismatch = self.check_parent_child_id_mismatch()
        parent_approved = self.check_parent_approved()
        # If user needs the list of imeis on the frontend we can show it.
        if not self.validate_imei_per_device():
            errors['imei_per_device'] = [_("IMEIs per device count in file is not same as input.")]
        if not self.validate_device_count():
            errors['device_count'] = [_("Device count in file is not same as input")]
        if len(invalid_imeis) > 0:
            errors['invalid_imeis'] = [_("Invalid IMEIs in the input file")]
        if len(duplicate_imeis['IMEIs']) > 0:
            errors['duplicate_imeis'] = [_("Duplicate IMEIs in the input file")]
        if missing_imeis:
            errors['missing_imeis'] = [_("Some IMEIs are missing in the columns")]
        if not rows_limit:
            errors['limit'] = [_("Rows limit is 10000000 for single request")]
        if len(invalid_format) > 0:
            errors['invalid_format'] = [_("Invalid IMEIs Format in input file")]
        if parent_child_mismatch:
            errors['parent_child_imeis_mismatch'] = [_("IMEIs from input file mismatched with main registration file.")]
        if parent_child_id_mismatch:
            errors['parent_child_id_mismatch'] = [_("Only the user that applied for parts is authorized to apply.")]
        if parent_approved:
            errors['parent_approved'] = [_("Parts application must be processed and approved before applying for assembled devices.")]
        return errors

    def validate_de_registration(self):
        """Method to validate de registration data."""
        errors = {}
        invalid_imeis = self.get_invalid_imeis()
        duplicate_imeis = self.get_duplicate_imeis()
        invalid_format = self.check_imei_format()
        if not self.validate_device_count():
            errors['device_count'] = [_("Device count in file is not same as input")]
        if len(invalid_imeis) > 0:
            errors['invalid_imeis'] = [_("Invalid IMEIs in the input file")]
        if len(duplicate_imeis['IMEIs']) > 0:
            errors['duplicate_imeis'] = [_("Duplicate IMEIs in the input file")]
        if len(invalid_format) > 0:
            errors['invalid_format'] = [_("Invalid IMEIs Format in input file")]
        return errors

    def process(self, request_type):
        """Method to start the main process."""
        if request_type == 'registration':
            errors = self.validate_registration()
        elif request_type == 'assembled_registration':
            errors = self.validate_assembled_registration()
        else:
            errors = self.validate_de_registration()
        response = errors if errors else self.transform_data(request_type)
        return response

