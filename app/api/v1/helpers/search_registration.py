"""
DRS Registration search package.
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
from datetime import datetime, timedelta
from marshmallow.utils import isoformat

from flask import Response

from app import app, db
from app.api.v1.helpers.pagination import Pagination
from app.api.v1.helpers.response import MIME_TYPES, CODES


class SearchRegistraion:
    """Class for searching registration data in database."""

    def __init__(self):
        """Constructor."""

    @staticmethod
    def format_response(data):
        """Method to transform data into a json compatible response."""
        results = []
        for d in data:
            response = {
                "id": d.get("id"),
                "tracking_id": d.get('tracking_id'),
                "status": d.get('status'),
                "report": d.get('report'),
                "report_status_label": d.get('processing_status'),
                "processing_status_label": d.get('report_status'),
                "request_type": d.get('request_type'),
                "created_at": isoformat(d.get('created_at')) if d.get('created_at') else 'N/A',
                "updated_at": isoformat(d.get('updated_at')) if d.get('updated_at') else 'N/A',
                "creator": {
                    "user_id": d.get('user_id'),
                    "user_name": d.get('user_name')
                },
                "reviewer": {
                    "user_id": d.get('reviewer_id') if d.get('reviewer_id') else 'N/A',
                    "user_name": d.get('reviewer_name') if d.get('reviewer_name') else 'N/A'
                },
                "device_details":
                    {
                        "brand": d.get('brand') if d.get('brand') else 'N/A',
                        "model_name": d.get('model_name') if d.get('model_name') else 'N/A',
                        "operating_system": d.get('operating_system') if d.get('operating_system') else 'N/A',
                        "device_type": d.get('device_type') if d.get('device_type') else 'N/A',
                        "imeis": d.get('imeis').split(',') if d.get('imeis') else 'N/A',
                        "device_count": d.get('device_count') if d.get('device_count') else 'N/A',
                        "technologies": d.get('technologies') if d.get('technologies') else 'N/A'
                    }
            }
            results.append(response)
        return results

    @staticmethod
    def get_result(request, group=None):
        """Method to get search data from the database."""
        args = request.get_json()
        request_data = args.get("search_args")
        count = len(request_data)
        search_specs = args.get("search_specs")
        start = 1 if args.get('start') < 1 else args.get('start', 1)
        limit = 10 if args.get('limit') < 1 else args.get('limit', 10)

        sql = "select * from search_registration"

        try:
            if count == 0:
                if group:
                    if group == 'reviewer':
                        data = db.engine.execute(
                            sql + " where status<>'New Request' and status<>'Awaiting Documents' and status<>'Closed' "
                                  "order by updated_at desc")
                    elif (group == 'individual' or group == 'importer') and bool(search_specs['user_id']):
                        data = db.engine.execute(
                            sql + " where user_id = '{val}' order by updated_at desc".format(
                                val=search_specs['user_id']))
                requests = []
                for row in data:
                    requests.append(dict((col, val) for col, val in row.items()))
                if requests:
                    paginated_data = Pagination.get_paginated_list(requests, '/search', start=start,
                                                                   limit=limit)

                    paginated_data['requests'] = SearchRegistraion.format_response(paginated_data['requests'])
                    response = Response(json.dumps(paginated_data, default=str), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                    return response
            else:

                if group:
                    if group == 'reviewer':
                        sql = sql + " where status <> 'New Request' and status <> 'Awaiting Documents' and status <> 'Closed' AND"
                    elif (group == 'individual' or group == 'importer') and bool(search_specs['user_id']):
                        sql = sql + " where user_id = '{val}' AND".format(val=search_specs['user_id'])
                for x in request_data:
                    count = count - 1
                    if count == 0:
                        if x == "updated_at" or x == "created_at":
                            date = request_data.get(x).split(",")
                            sql = sql + " {col} between '{min}' AND '{max}'".format(
                                col=x,
                                min=date[0],
                                max=datetime.strptime(date[1], "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)
                            )

                        elif x == 'id':
                            data = request_data.get(x)
                            sql = sql + " {col}={val}".format(col=x, val=data)

                        elif x == 'device_count':
                            data = request_data.get(x)
                            sql = sql + " {col}='{val}'".format(col=x, val=data)

                        elif x == "imeis":
                            record_len = len(request_data.get(x))
                            if record_len == 1:
                                sql = sql + " {col} like '%%{val}%%'".format(
                                    col=x,
                                    val=request_data.get(x)[0]
                                )
                            if record_len > 1:
                                sql = sql + "("
                                for val in request_data.get(x):
                                    record_len = record_len - 1
                                    if record_len == 0:
                                        sql = sql + " {col} like '%%{val}%%')".format(
                                            col=x,
                                            val=val
                                        )
                                    else:
                                        sql = sql + " {col} like '%%{val}%%' OR".format(
                                            col=x,
                                            val=val
                                        )

                        elif x == "technologies":

                            record_len = len(request_data.get(x))

                            if record_len == 1:
                                sql = sql + " {col} ilike '%%{val}%%'".format(

                                    col=x,

                                    val=request_data.get(x)[0]

                                )

                            if record_len > 1:
                                sql = sql + "("
                                for val in request_data.get(x):

                                    record_len = record_len - 1

                                    if record_len == 0:

                                        sql = sql + " {col} ilike '%%{val}%%')".format(

                                            col=x,

                                            val=val

                                        )

                                    else:

                                        sql = sql + " {col} ilike '%%{val}%%' OR".format(

                                            col=x,

                                            val=val

                                        )

                        else:
                            sql = sql + " {col} ilike '%%{val}%%'".format(
                                col=x,
                                val=request_data.get(x)
                            )
                    else:
                        if x == "updated_at" or x == "created_at":
                            date = request_data.get(x).split(",")
                            sql = sql + " {col} between '{min}' AND '{max}' AND".format(
                                col=x,
                                min=date[0],
                                max=datetime.strptime(date[1], "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)
                            )

                        elif x == 'id':
                            data = request_data.get(x)
                            sql = sql + " {col}={val} AND".format(col=x, val=data)

                        elif x == 'device_count':
                            data = request_data.get(x)
                            sql = sql + " {col}='{val}' AND".format(col=x, val=data)

                        elif x == "imeis":
                            record_len = len(request_data.get(x))
                            if record_len == 1:
                                sql = sql + " {col} like '%%{val}%%' AND".format(col=x, val=request_data.get(x)[0]
                                                                                 )
                            if record_len > 1:
                                sql = sql + "("
                                for val in request_data.get(x):
                                    record_len = record_len - 1
                                    if record_len == 0:
                                        sql = sql + " {col} like '%%{val}%%') AND".format(
                                            col=x,
                                            val=val
                                        )
                                    else:
                                        sql = sql + " {col} like '%%{val}%%' OR".format(
                                            col=x,
                                            val=val
                                        )

                        elif x == "technologies":
                            record_len = len(request_data.get(x))
                            if record_len == 1:
                                sql = sql + " {col} ilike '%%{val}%%' AND".format(

                                    col=x,

                                    val=request_data.get(x)[0]

                                )

                            if record_len > 1:
                                sql = sql + "("
                                for val in request_data.get(x):

                                    record_len = record_len - 1

                                    if record_len == 0:

                                        sql = sql + " {col} ilike '%%{val}%%') AND".format(

                                            col=x,

                                            val=val

                                        )

                                    else:

                                        sql = sql + " {col} like '%%{val}%%' OR".format(

                                            col=x,

                                            val=val

                                        )

                        else:
                            sql = sql + " {col} ilike '%%{val}%%' AND".format(
                                col=x,
                                val=request_data.get(x)
                            )
                sql = sql + " order by updated_at desc"
                data = db.session.execute(sql)
                requests = []
                for row in data:
                    requests.append(dict((col, val) for col, val in row.items()))
                if requests:
                    paginated_data = Pagination.get_paginated_list(requests, '/search', start=start,
                                                                   limit=limit)

                    paginated_data['requests'] = SearchRegistraion.format_response(paginated_data['requests'])
                    response = Response(json.dumps(paginated_data, default=str), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                    return response
                else:
                    data = {
                        "start": start,
                        "previous": "",
                        "next": "",
                        "requests": requests,
                        "count": 0,
                        "limit": limit
                    }
                    response = Response(json.dumps(data, default=str), status=CODES.get("OK"),
                                        mimetype=MIME_TYPES.get('APPLICATION_JSON'))
                    return response
        except Exception as e:
            app.logger.exception(e)
            data = {
                "start": start,
                "previous": "",
                "next": "",
                "requests": [],
                "count": 0,
                "limit": limit,
                "message": "Not Found"
            }
            response = Response(json.dumps(data), status=CODES.get("NOT_FOUND"),
                                mimetype=MIME_TYPES.get('APPLICATION_JSON'))
            return response
