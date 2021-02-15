"""
DRS healthcheck resource module.
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
import uuid
import requests

from pprint import pprint

from flask import Response, request
from flask_apispec import marshal_with, doc, MethodResource
from flask_restful import Resource
from flask_babel import lazy_gettext as _
from datetime import datetime
from urllib.parse import quote, unquote


from app import app, db
from app.api.v1.models.regdetails import RegDetails
from app.api.v1.schema.ussd import RegistrationDetailsSchema

from app.api.v1.helpers.response import MIME_TYPES, CODES
from app.api.v1.helpers.utilities import Utilities

from app.metadata import version, db_schema_version
from app.api.v1.schema.version import VersionSchema

from app.api.v1.helpers.key_cloak import Key_cloak
from app.api.v1.helpers.sms import Jasmin

from app.api.v1.schema.reviewer import ErrorResponse
from marshmallow import Schema, fields, validates, ValidationError, post_dump, validate, pre_dump


class Send(MethodResource):
    """Class for handling version api resources."""

    def get(self):
        """GET method handler."""
        return Response(json.dumps(
            VersionSchema().dump(dict(
                version=version,
                db_schema_version=db_schema_version
            )).data))

    def post(self):
        print("Are we in the send API Call")
        sender = '03337372337'
        network = 'ufone-smpp'
        message = "This is the test message to be send to the user"
        jasmin_send_response = Jasmin.send(sender, network, message)
        print(jasmin_send_response)
        return Response(json.dumps(
            VersionSchema().dump(dict(
                version=version,
                db_schema_version=db_schema_version
            )).data))


class SendBatchTest(MethodResource):
    """Class for handling version api resources."""

    def get(self):
        """GET method handler."""
        return Response(json.dumps(
            VersionSchema().dump(dict(
                version=version,
                db_schema_version=db_schema_version
            )).data))

    def post(self):
        print("Are we in the Send Batch Post call")

        messages_list = []
        messages = {
            'from': 'sender_name',
            'to': '03331234567',
            'content': 'Lorum Ipsum'
        }
        messages_list.append(messages.copy())

        jasmin_send_response = Jasmin.send_batch(messages_list, network='ufone')
        print(jasmin_send_response)
        return Response(json.dumps(
            VersionSchema().dump(dict(
                version=version,
                db_schema_version=db_schema_version
            )).data))


class Ussd_Script(MethodResource):
    """Class for handling USSD HTTP requests for APIs."""
    headers = {'Content-Type': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    network_list = {"ufone", "jazz", "zong", "telenor"}
    imei_min = 14
    imei_max = 16
    device_count = 1

    # database stuff
    database = 'jasmin'
    user = 'postgres'
    password = 'postgres'
    host = '192.168.100.42'
    port = '5432'

    def get(self):
        argv = request.args.to_dict()

        scenario = self.case_search(int(argv['case']))
        argv['scenario'] = str(scenario)
        argv['msisdn'] = self.validate_msisdn(argv['msisdn'])

        if scenario == "registration":
            resp = self.registration(argv)
        elif scenario == "track_record":
            resp = self.tracking(argv)
        elif scenario == "delete_record":
            resp = self.delete_record(argv)
        elif scenario == "count_records":
            resp = self.count_records(argv)
        else:
            print("API not found")
            return False

        """GET method handler."""
        if resp:
            content = (resp.content).decode()
        else:
            content = {"Invalid data passed"}
        print(content)
        return Response(content, status=CODES.get('OK'),
                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))

    @staticmethod
    def validate_msisdn(sender_no):
        if sender_no[0:3] == '%2B':
            sender_no = sender_no[3:]
        elif sender_no[0:4] == '0092':
            sender_no = '0' + sender_no[4:]
        elif sender_no[0:3] == '+92':
            sender_no = '0' + sender_no[3:]
        elif sender_no[0:2] == '92':
            sender_no = '0' + sender_no[2:]
        elif sender_no[0:1] == '3':
            sender_no = '03' + sender_no[1:]
        return sender_no

    # validation method
    def data_validation(self, argv):
        if argv['case'] == '1':
            if self.is_integer(argv['msisdn']):  # phone number validation
                if argv['network'] in self.network_list:  # network defined in the list ???
                    if self.is_integer(argv['cnic']):  # CNIC integer
                        # validating IMEIs
                        imeis_str = unquote(argv['imeis'])
                        imeis = [x.strip() for x in imeis_str.split(',')]
                        for imei in imeis:
                            if len(imei) < self.imei_min or len(imei) > self.imei_max:
                                print("IMEI can not be less than " + str(self.imei_min) + " and greater than " + str(self.imei_max))
                                print(imei)
                                return False
                            else:
                                return True
                    else:
                        print(argv['msisdn'] + " Not valid CNIC number ")
                        return False
                else:
                    print(argv['network'] + " Not found in the list ")
                    print(self.network_list)
                    return False
            else:
                print("phone number must be digits.")
                return False
        elif argv['case'] == '2':
            if self.is_integer(argv['msisdn']):  # phone number validation
                if argv['network'] in self.network_list:  # network defined in the list ???
                    if self.is_integer(argv['device_id']):  # device number integer
                        return True
                    else:
                        print(argv['device_count'] + " Not valid device number ")
                        return False
                else:
                    print(argv['network'] + " Not found in the list ")
                    print(self.network_list)
                    return False
            else:
                print("phone number must be digits.")
                return False
        elif argv['case'] == '3':
            print("delete validation")
            if self.is_integer(argv['msisdn']):  # phone number validation
                if argv['network'] in self.network_list:  # network defined in the list ???
                    if self.is_integer(argv['device_id']):  # device number integer
                        if argv['close_request'] == 'True' or argv['close_request'] == 'False':
                            return True
                        else:
                            print("close_request can either be true or false")
                            return False
                    else:
                        print(argv['device_id'] + " Not valid device number ")
                        return False
                else:
                    print(argv['network'] + " Not found in the list ")
                    print(self.network_list)
                    return False
            else:
                print("phone number must be digits.")
                return False
        elif argv['case'] == '4':
            print("count validation")
            if self.is_integer(argv['msisdn']):  # phone number validation
                if argv['network'] in self.network_list:  # network defined in the list ???
                    return True
                else:
                    print(argv['network'] + " Not found in the list ")
                    print(self.network_list)
                    return False
            else:
                print("phone number must be digits.")
                return False

    # validates, make parameters and hit registration API
    def registration(self, argv):
        imeis_list = []
        valid = self.data_validation(argv)
        if valid == True:

            db_response = self.dump_to_db(argv)

            if db_response == True:
                msisdn = argv['msisdn']
                network = argv['network']
                cnic = argv['cnic']
                imeis_str = unquote(argv['imeis'])
                imeis = [x.strip() for x in imeis_str.split(',')]
                imeis_list.append(imeis)

                url = str(app.config['BASE_URL'] + app.config['API_VERSION_V1'] + "/register_ussd")

                payload = {'msisdn': msisdn, 'network': network, 'cnic': int(cnic), 'imeis': str(imeis_list),
                           'device_count': self.device_count}
                response = requests.post(url=str(url), data=payload, headers=self.headers)

                return response
            else:
                print("Error in database connection. Please check dump_to_db function")
                return False

        else:
            print("Invalid data passed for registration.")
            return False

    def tracking(self, argv):
        valid = self.data_validation(argv)
        if valid == True:

            db_response = self.dump_to_db(argv)
            if db_response == True:
                msisdn = argv['msisdn']
                network = argv['network']
                device_id = argv['device_id']

                url = str(app.config['BASE_URL'] + app.config['API_VERSION_V1'] + "/track_record_ussd")
                # url = str("http://127.0.0.1:5000/api/v1/track_record_ussd")

                payload = {"msisdn": msisdn, "network": network, "device_id": device_id}

                response = requests.post(url=str(url), data=payload, headers=self.headers)

                return response
            else:
                print("Error in database connection. Please check dump_to_db function")
                return False

        else:
            print("Invalid data passed for tracking. Please pass msisdn, network and device_id")
            return False

    def delete_record(self, argv):
        valid = self.data_validation(argv)
        if valid == True:

            db_response = self.dump_to_db(argv)
            if db_response == True:

                msisdn = argv['msisdn']
                network = argv['network']
                device_id = argv['device_id']
                close_request = argv['close_request']

                url = str(app.config['BASE_URL'] + app.config['API_VERSION_V1'] + "/delete_record_ussd")
                # url = str("http://127.0.0.1:5000/api/v1/delete_record_ussd")

                payload = {"msisdn": msisdn, "network": network, "device_id": device_id, "close_request": close_request}
                response = requests.put(url=str(url), data=payload, headers=self.headers)
                return response
            else:
                print("Error in database connection. Please check dump_to_db function")
                return False

        else:
            print(
                "Invalid data passed for deleting. Please pass msisdn, network, device_id and close_request in the parameters")
            return False

    def count_records(self, argv):
        valid = self.data_validation(argv)
        if valid == True:

            db_response = self.dump_to_db(argv)
            if db_response == True:

                msisdn = argv['msisdn']
                network = argv['network']

                url = str(app.config['BASE_URL'] + app.config['API_VERSION_V1'] + "/ussd_records_count")
                # url = str("http://127.0.0.1:5000/api/v1/ussd_records_count")

                payload = {"msisdn": msisdn, "network": network}
                response = requests.post(url=str(url), data=payload, headers=self.headers)

                return response
            else:
                print("Error in database connection. Please check dump_to_db function")
                return False

        else:
            print("Invalid data passed for count API. Please pass msisdn and network.")
            return False

    @staticmethod
    def is_integer(n):
        try:
            float(n)
        except ValueError:
            return False
        else:
            return float(n).is_integer()

    @staticmethod
    def case_search(menu_code):
        case = ""
        if menu_code 	== 1: case = "registration"
        elif menu_code 	== 2: case = "track_record"
        elif menu_code 	== 3: case = "delete_record"
        elif menu_code 	== 4: case = "count_records"

        return case


    # @staticmethod
    def dump_to_db(self, argv):
        import psycopg2
        conn = psycopg2.connect(database = self.database, user = self.user, password = self.password, host = self.host, port = self.port)

        if conn:
            now = datetime.now()
            current_t = now.strftime("%H:%M:%S")
            from_user = str(argv['msisdn'])

            cur = conn.cursor()
            sql = 'INSERT INTO sms_mo ("from", "to", origin_connector, priority, coding, validity, content) VALUES (%s,%s,%s,%s,%s,%s,%s)'
            val = (from_user, '', argv['network'], '', argv['case'], current_t,  json.dumps(argv))
            cur.execute(sql, val)
            conn.commit()
            conn.close()

            return True
        else:
            print("Database Connection failed. Please check the parameters.")
            return False

'''
for registration 
	http://127.0.0.1:5000/api/v1/ussd_script?case=1&msisdn=03337372337&network=ufone&cnic=1710182665313&imeis=356468061158625,356468061157453

for tracking record 
    http://127.0.0.1:5000/api/v1/ussd_script?case=2&msisdn=03337372337&network=ufone&device_id=400

for deleting record 
    http://127.0.0.1:5000/api/v1/ussd_script?case=3&msisdn=03337372337&network=ufone&device_id=400&close_request=True

for counting record 
    http://127.0.0.1:5000/api/v1/ussd_script?case=4&msisdn=03337372337&network=ufone
'''