"""
Copyright (c) 2018-2020 Qualcomm Technologies, Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
    The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
    Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
    This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                               #
"""
from elasticsearch import Elasticsearch
from app import app
from datetime import datetime
from app.api.v1.models.status import Status

from flask_script import Command


class EsIndex(Command):

    def __init__(self):
        super().__init__()
        self.es = Elasticsearch([{'host': app.config['es']['Host'], 'port': app.config['es']['Port']}])

    def __create_es_index(self):
        mapping = '''{
                    "mappings": {
                    "numeric_detection": false,
                    "properties": {
                      "updated_at": {
                        "type": "date",
                        "format": "yyyy-MM-dd HH:mm:ss" 
                      },
                      "created_at": {
                        "type": "date",
                        "format": "yyyy-MM-dd HH:mm:ss" 
                      }
                    }
                    }
                    }'''
        self.es.indices.delete(index=app.config['es']['Index'], ignore=[400, 404])
        print(self.es.indices.create(index=app.config['es']['Index'], body=mapping, ignore=400))

    def run(self):
        self.__create_es_index()


class EsLog:

    @staticmethod
    def new_request_serialize(log_data, request_type, imeis=None, method=None, dereg=None):

        date = datetime.now()
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        es_lang = {"lang": "painless"}
        description = "New Request created by "

        if dereg:
            description = "Deregistration request created by "
            if method is not None and method.lower() == 'put':
                if log_data.status == 8:
                    description = "De-registration request closed by "
                else:
                    description = "De-registration request updated by "

            log = {
                "script": es_lang,
                "reg_id": log_data["id"],
                "tracking_id": log_data["tracking_id"],
                "user_name": log_data["user_name"],
                "user_id": log_data["user_id"],
                "status": log_data['status_label'],
                "request_type": request_type,
                "imeis": imeis,
                "reviewer_id": log_data["reviewer_id"],
                "reviewer_name": log_data["reviewer_name"],
                "method": method,
                "created_at": date,
                "description": description + log_data['user_name']
            }

            return log

        if method is not None and method.lower() == "put":
            if log_data.status == 8:
                description = "Request closed by "
            else:
                description = "Request updated by "

            log = {
                "script": es_lang,
                "reg_id": log_data.id,
                "tracking_id": log_data.tracking_id,
                "user_name": log_data.user_name,
                "user_id": log_data.user_id,
                "status": Status.get_status_type(log_data.status),
                "request_type": request_type,
                "imeis": imeis,
                "reviewer_id": log_data.reviewer_id,
                "reviewer_name": log_data.reviewer_name,
                "method": method,
                "updated_at": date,
                "description": description + log_data.user_name
            }
        else:
            log = {
                "script": es_lang,
                "reg_id": log_data["id"],
                "tracking_id": log_data["tracking_id"],
                "user_name": log_data["user_name"],
                "user_id": log_data["user_id"],
                "status": log_data['status_label'],
                "request_type": request_type,
                "imeis": imeis,
                "reviewer_id": log_data["reviewer_id"],
                "reviewer_name": log_data["reviewer_name"],
                "method": "Post",
                "created_at": date,
                "description": description + log_data['user_name']
            }

        return log

    @staticmethod
    def new_device_serialize(log_data, request_type, regdetails=None, imeis=None, reg_status=None, method=None,
                             dereg=False):

        date = datetime.now()
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        es_lang = {"lang": "painless"}
        description = "New Device created by "
        devices = []

        if dereg:
            if method is not None and method.lower() == "put":
                description = "Device data updated by "

            for device in log_data:
                device_info = {
                    "device_id": device['id'],
                    "brand": device['brand_name'],
                    "model": device['model_name'],
                    "model_number": device['model_num']
                }
                devices.append(device_info)

            log = {
                "script": es_lang,
                "devices": devices,
                "reg_id": regdetails.id,
                "tracking_id": regdetails.tracking_id,
                "user_name": regdetails.user_name,
                "user_id": regdetails.user_id,
                "status": reg_status,
                "request_type": request_type,
                "method": method,
                "created_at": date,
                "description": description + regdetails.user_name + " for De-Registration request id "
                                   + str(regdetails.id)
                }

            return log

        if method is not None and method.lower() == "put":
            description = "Device updated by "

        device_info = {
            "device_id": log_data['id'],
            "brand": log_data['brand'],
            "model": log_data['model_name'],
            "model_number": log_data['model_num']
        }

        log = {
            "script": es_lang,
            "devices": device_info,
            "reg_id": regdetails.id,
            "tracking_id": regdetails.tracking_id,
            "user_name": regdetails.user_name,
            "user_id": regdetails.user_id,
            "status": reg_status,
            "request_type": request_type,
            "method": method,
            "created_at": date,
            "description": description + regdetails.user_name + " for Registration request id "
                           + str(log_data["reg_details_id"])
        }

        return log

    @staticmethod
    def new_doc_serialize(log_data, request_type, regdetails =None, imeis=None, reg_status=None, method=None,
                          request=None):

        date = datetime.now()
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        es_lang = {"lang": "painless"}
        documents = []
        description = "New Documents created by " + regdetails.user_name \
                      + " for " + request + " request id " + str(regdetails.id)

        if method is not None and method.lower() == "put":
            description = "Documents updated by " + regdetails.user_name \
                          + " for " + request + " request id " + str(regdetails.id)

        for doc in log_data:
            doc_info = {
                "document_id": doc['id'],
                "label": doc['label'],
                "filename": doc['filename'],
                "link": doc['link']
            }
            documents.append(doc_info)

        log = {
            "script": es_lang,
            "document_info": documents,
            "reg_id": regdetails.id,
            "tracking_id": regdetails.tracking_id,
            "user_name": regdetails.user_name,
            "user_id": regdetails.user_id,
            "status": reg_status,
            "request_type": request_type,
            "method": method,
            "created_at": date,
            "description": description
        }

        return log

    @staticmethod
    def insert_log(log):
        es = Elasticsearch([{'host': app.config['es']['Host'], 'port': app.config['es']['Port']}])
        return es.index(index=app.config['es']['Index'], doc_type="_doc", body=log)

    @staticmethod
    def reviewer_serialize(reviewer, method=None, review_type = None, request_details=None, section=None, status=None,
                           description=None):

        date = datetime.now()
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        es_lang = {"lang": "painless"}

        reviewer_data = {
            'reviewer_name': reviewer.get('reviewer_name'),
            'reviewer_id': reviewer.get('reviewer_id'),
            'request_type': reviewer.get('request_type'),
            'reg_id': reviewer.get('request_id')
        }

        if 'section' in reviewer:
            reviewer_data['section'] = reviewer.get('section')
            reviewer_data['section_status'] = reviewer.get('section_status')
            reviewer_data['comment'] = reviewer.get('comment')

        log = {
            "script": es_lang,
            "reviewer_info": reviewer_data,
            "reg_id": request_details.id,
            "tracking_id": request_details.tracking_id,
            "user_name": request_details.user_name,
            "user_id": request_details.user_id,
            "status": status,
            "request_type": review_type,
            "method": method,
            "created_at": date,
            "description": description
        }
        return log

    @staticmethod
    def auto_review(request, request_type, method, status):

        date = datetime.now()
        date = date.strftime("%Y-%m-%d %H:%M:%S")

        es_lang = {"lang": "painless"}

        reviewer_data = {
            'reviewer_name': 'Automated Process',
            'reviewer_id': '000',
            'request_type': request_type,
            'reg_id': request.id
        }

        log = {
            "script": es_lang,
            "reviewer_info": reviewer_data,
            "reg_id": request.id,
            "tracking_id": request.tracking_id,
            "user_name": request.user_name,
            "user_id": request.user_id,
            "status": status,
            "request_type": request_type,
            "method": method,
            "created_at": date,
            "description": "{req_type} created by {user} & Automatically {status} by System".format(
                req_type=request_type, user=request.user_name, status=status
            )
        }

        return log

