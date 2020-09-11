import os
from app import session, celery, app
from requests import ConnectionError
from app.api.v1.helpers.error_handlers import *
from app.api.v1.helpers.reports_generator import BulkCommonResources

from threading import Thread
from math import ceil

import pandas as pd
import uuid
import json


from flask_restful import Resource

class CoreConf(Resource):
    @staticmethod    
    def get():

        # return (app.config['conditions']['classification_state'])
        # print(config['conditions']['realtime_checks'])

        # for classification_state in app.config['conditions']['classification_state']:
            # print(classification_state['type'])
            # print(classification_state['name'])

        # exit()

        batch_req = {"imeis": "0990000862471854",
                    "include_registration_status": True,
                    "include_stolen_status": True
                    }
        headers = {'content-type': 'application/json', 'charset': 'utf-8', 'keep_alive': 'false'}
        imei_response = session.post('{}/imei-batch'.format(app.config['CORE_BASE_URL']+app.config['API_VERSION']), data=json.dumps(batch_req),headers=headers)
        imei_response = imei_response.json()
        # records.extend(imei_response['results'])
        records = imei_response['results']
        response = BulkCommonResources.build_drs_summary(records, 11)
        # # print(response)
        return response
        # exit()
 