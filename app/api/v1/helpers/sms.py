"""
DRS Reports generator package.
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
from app import session
from requests import ConnectionError
from app.api.v1.helpers.error_handlers import *
from app.api.v1.helpers.ussd_helper import Ussd_helper

import json

class Jasmin:
    @staticmethod
    def send(sender, network, message):
        try:
            url = str(app.config['JASMIN_URL'] + app.config['JASMIN_PORT']+app.config['JASMIN_INDIVIDUAL_SEND'])

            # message body
            sms_body = {
                "to": sender,
                "from": "DIRBS-DRS",
                "coding": 8,
                "content": message
            }

            # get operator authorization token
            network = Ussd_helper.return_operator_token(network)

            headers = {'content-type': 'application/json', 'Authorization': 'Basic '+str(network)}

            app.logger.info(url)
            jasmin_send_response = session.post(
                url=url,
                data=json.dumps(sms_body),
                headers=headers)

            if jasmin_send_response.status_code == 200:
                return jasmin_send_response
            else:
                print(jasmin_send_response)
                return app.logger.info("Jasmin status code other than 200")
        except (ConnectionError, Exception) as e:
            print("Jasmin Send API threw an Exception")
            app.logger.exception(e)


    @staticmethod
    def send_batch(messages_list, network):
        try:
            url = str(app.config['JASMIN_URL'] + app.config['JASMIN_PORT']+app.config['JASMIN_BATCH_SEND'])

            # get operator authorization token
            network = Ussd_helper.return_operator_token(network)

            sms_body = {"messages": messages_list}

            headers = {'content-type': 'application/json', 'Authorization': 'Basic ' + str(network)}
            # headers = {'content-type': 'application/json', 'Authorization': 'Basic Zm9vOmJhcg=='}

            jasmin_send_response = session.post(
                url=url,
                data=json.dumps(sms_body),
                headers=headers)

            if jasmin_send_response:
                if jasmin_send_response.status_code == 200:
                    return jasmin_send_response
                else:
                    app.logger.info(jasmin_send_response)
                    return jasmin_send_response
            else:
                print(jasmin_send_response)
                return app.logger.info(jasmin_send_response)
        except (ConnectionError, Exception) as e:
            print("Jasmin Send API threw an Exception")
            app.logger.exception(e)






