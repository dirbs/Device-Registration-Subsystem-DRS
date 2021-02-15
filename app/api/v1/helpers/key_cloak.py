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
import random, string

import json

class Key_cloak:
    @staticmethod
    def get_admin_token():
        try:
            url = str(app.config['KEYCLOAK_URL']+app.config['KEYCLOAK_PORT']+app.config['KEYCLOAK_TOKEN'])

            # batch dict for token
            req_data = {
                "username": "admin",
                "password": "admin123!",
                "grant_type": "password",
                "client_id": "admin-cli"
            }

            headers = {'content-type': 'application/x-www-form-urlencoded'}

            admin_token_response = session.post(
                url=url,
                data=req_data,
                headers=headers)

            if admin_token_response.status_code == 200:
                admin_response_json = admin_token_response.json()
                return admin_response_json
            else:
                return app.logger.info("Get Admin Token failed due to status other than 200")
        except (ConnectionError, Exception) as e:
            app.logger.exception(e)

    @staticmethod
    def check_user_get_data(args, admin_token_data):

        try:
            # search for a user
            user_info = Key_cloak.check_user(args, admin_token_data)
            if user_info == False:

                # if user does not exist, create user
                created_user = Key_cloak.create_user(args, admin_token_data)
                if created_user == True:

                    # get the newly created user id
                    created_user_info = Key_cloak.check_user(args, admin_token_data)

                    # user created, set the user id for API calls
                    user_id = {"id": created_user_info['id']}
                    args.update(user_id)

                    # user created, set the user_id for DB insertion later on
                    user_id = {"user_id": created_user_info['id']}
                    args.update(user_id)

                    # assign password to newly created user
                    password_response_args = Key_cloak.assign_password(args, admin_token_data)

                    # assign group to the newly created user
                    group_response_args = Key_cloak.assign_group(password_response_args, admin_token_data)
                    if group_response_args == False:
                        return False
                    else:
                        print("Printing the created user with password and group dict")
                        print(password_response_args)
                        return password_response_args

                else:
                    # print("user could not be created API responded with False")
                    app.logger.info("User could not be created API responded with False.")

            else:
                # if user exists, return
                return user_info

        except (ConnectionError, Exception) as e:
            # print("exception executed in second call")
            app.logger.exception(e)

    @staticmethod
    def check_user(args, admin_token_data):

        url = str(app.config['KEYCLOAK_URL']+app.config['KEYCLOAK_PORT']+app.config['KEYCLOAK_SEARCH']) + args['cnic']

        headers = {'Authorization': 'bearer ' + admin_token_data['access_token']}

        user_info = session.get(
            url=url,
            headers=headers)
        if user_info.status_code == 200:
            user_info_object = user_info.json()

            # if user is available, return the userdata, else make user with the parameters and return the data
            if not user_info_object:
                return False

            else:
                # return the user
                user_info_object[0]["user_id"] = user_info_object[0]["id"]
                return user_info_object[0]
        else:
            app.logger.info("Check user API failed due to status other than 200")


    @staticmethod
    def create_user(args, admin_token_data):
        try:
            url = str(app.config['KEYCLOAK_URL'] + app.config['KEYCLOAK_PORT'] + app.config['KEYCLOAK_USERS'])

            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'bearer '+admin_token_data['access_token'],
                'Connection': 'keep-alive'
            }

            # Dictionary for creating new user
            create_user_data = {
                "firstName": args['cnic'],
                "email": args['cnic']+'@dirbs.com',
                "enabled": "true",
                "username": args['cnic']
            }

            new_user_info = session.post(
                url=url,
                data=json.dumps(create_user_data),
                headers=headers)
            if new_user_info.status_code == 201:    # 201 for user creation
                # print('New user created with status 201')
                return True
            else:
                app.logger.info("create_user_and_return API failed due to status other than 201")
                return False

        except (ConnectionError, Exception) as e:
            # print("exception executed in third call")
            app.logger.exception(e)

    @staticmethod
    def assign_password(args, admin_token_data):
        password = Key_cloak.password_generator(8)

        # add password to args so that messages may be shifted to user through SMSC
        pass_dict = {"password": password}
        args.update(pass_dict)

        url = str(app.config['KEYCLOAK_URL'] + app.config['KEYCLOAK_PORT'] + app.config['KEYCLOAK_USERS'] + '/'
                  +args['id']+app.config['KEYCLOAK_RESET_PASSWORD'])



        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'bearer ' + admin_token_data['access_token'],
            'Connection': 'keep-alive'
        }

        # Dictionary for setting password data
        password_dict = {
            "type": 'password',
            "value": password,
            "temporary": "False"
        }

        updated_user_info = session.put(
            url=url,
            data=json.dumps(password_dict),
            headers=headers)

        if updated_user_info.status_code == 204:    # 204 for keycloak response in case of password update success
            return args
        else:
            app.logger.info("check user API failed due to status other than 204")
            return False

    @staticmethod
    def assign_group(password_response_args, admin_token_data):

        url = str(app.config['KEYCLOAK_URL'] + app.config['KEYCLOAK_PORT'] + app.config['KEYCLOAK_USERS'] + '/'
                  + password_response_args['id'] +'/groups/'+ app.config['KEYCLOAK_GROUP_ID'])

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'bearer ' + admin_token_data['access_token'],
            'Connection': 'keep-alive'
        }

        # Dictionary for setting group data
        group_dict = {
            "realm": 'DIRBS',
            "userId": password_response_args['id'],
            "groupId": str(app.config['KEYCLOAK_GROUP_ID'])
        }

        updated_user_info = session.put(
            url=url,
            data=json.dumps(group_dict),
            headers=headers)

        if updated_user_info.status_code == 204:    # 204 for keycloak response in case of group update success
            return password_response_args
        else:
            app.logger.info("check user API failed due to status other than 204")
            return False

    @staticmethod
    def password_generator(pass_length):

        password_length = int(pass_length)

        if app.config['USSD_PASSWORD_STRENGTH']:
            password_characters = string.ascii_letters + string.digits + string.punctuation
        else:
            password_characters = string.ascii_letters + string.digits
        password = []
        for x in range(password_length):
            password.append(random.choice(password_characters))

        return ("".join(password))