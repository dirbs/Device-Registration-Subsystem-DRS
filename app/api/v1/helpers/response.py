"""
DRS response package.
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

CODES = {
        "CONTINUE": 100,
        "SWITCHING_PROTOCOLS": 101,
        "PROCESSING": 102,
        "OK": 200,
        "CREATED": 201,
        "ACCEPTED": 202,
        "NON_AUTHORITATIVE_INFORMATION": 203,
        "NO_CONTENT": 204,
        "RESET_CONTENT": 205,
        "PARTIAL_CONTENT": 206,
        "MULTI_STATUS": 207,
        "ALREADY_REPORTED": 208,
        "IM_USED": 226,
        "MULTIPLE_CHOICES": 300,
        "MOVED_PERMANENTLY": 301,
        "FOUND": 302,
        "SEE_OTHER": 303,
        "NOT_MODIFIED": 304,
        "USE_PROXY": 305,
        "TEMPORARY_REDIRECT": 307,
        "PERMANENT_REDIRECT": 308,
        "BAD_REQUEST": 400,
        "UNAUTHORIZED": 401,
        "PAYMENT_REQUIRED": 402,
        "FORBIDDEN": 403,
        "NOT_FOUND": 404,
        "METHOD_NOT_ALLOWED": 405,
        "NOT_ACCEPTABLE": 406,
        "PROXY_AUTHENTICATION_REQUIRED": 407,
        "REQUEST_TIMEOUT": 408,
        "CONFLICT": 409,
        "GONE": 410,
        "LENGTH_REQUIRED": 411,
        "PRECONDITION_FAILED": 412,
        "REQUEST_ENTITY_TOO_LARGE": 413,
        "REQUEST_URI_TOO_LONG": 414,
        "UNSUPPORTED_MEDIA_TYPE": 415,
        "REQUEST_RANGE_NOT_SATISFIABLE": 416,
        "EXPECTATION_FAILED": 417,
        "UNPROCESSABLE_ENTITY": 422,
        "LOCKED": 423,
        "FAILED_DEPENDENCY": 424,
        "UPGRADE_REQUIRED": 426,
        "PRECONDITION_REQUIRED": 428,
        "TOO_MANY_REQUESTS": 429,
        "REQUEST_HEADER_FIELDS_TOO_LARGE": 431,
        "INTERNAL_SERVER_ERROR": 500,
        "NOT_IMPLEMENTED": 501,
        "BAD_GATEWAY": 502,
        "SERVICE_UNAVAILABLE": 503,
        "GATEWAY_TIMEOUT": 504,
        "HTTP_VERSION_NOT_SUPPORTED": 505,
        "VARIANT_ALSO_NEGOTIATES": 506,
        "INSUFFICIENT_STORAGE": 507,
        "LOOP_DETECTED": 508,
        "NOT_EXTENDED": 510,
        "NETWORK_AUTHENTICATION_REQUIRED": 511
    }

MESSAGES = {
        "RESOURCE_NOT_FOUND": "resource not found",
        "METHOD_NOT_ALLOWED": "method not allowed",
        "INVALID_USER": "invalid user",
        "INVALID_PARAM": "invalid parameter",
        "UNDEFINED_ID": "id was not defined",
        "INTERNAL_SERVER_ERROR": "internal server error"
    }

MIME_TYPES = {
    "APPLICATION_JSON": "application/json",
    "TEXT_PLAIN": "text/plain",
    "APPLICATION_ALL": "application/*"
}

RESPONSES = {
    'NOT_FOUND': 404,
    'BAD_REQUEST': 400,
    'OK': 200,
    'NO_CONTENT': 204,
    'INTERNAL_SERVER_ERROR': 500,
    'SERVICE_UNAVAILABLE': 503,
    'TIMEOUT': 504,
    'METHOD_NOT_ALLOWED': 405
}
