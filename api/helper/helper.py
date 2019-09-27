from datetime import datetime
from hashlib import sha512
from random import choice
from jose import jwt
import json
import logging
from datetime import datetime, date, timedelta
from flask import Response
import os
import uuid
import string
import random
from api.helper.constants import key_word

#from api.model.user import User
import api.model.user


def random_string(size):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(size)])


def now():
    return datetime.now()


def new_salt():
    source = [chr(x) for x in range(32, 127)]
    salt = u''.join(choice(source) for x in range(0, 32))

    return salt


def new_psw(salt, password):

    password = str(sha512(u'{0}{1}'.format(password, salt).encode('utf-8', 'ignore')).hexdigest())

    return password


def security_token(username, role_name):
    signed = jwt.encode(
        {'userName': '{0}'.format(username),
         'role': '{0}'.format(role_name)
         }, 'miha_zmaj', algorithm='HS256')

    return signed


"""def ok_response(message, additional_data=None):
    data = {
        'status': 'OK',
        'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
        'code': 200,
        'message': message,
        'data': additional_data if additional_data else {}
    }
    response = Response(json.dumps(data),
                        mimetype='application/json',
                        status=200)

    return response"""


def error_handler(error_status, message):
    data = {
            'status': 'ERROR',
            'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
            'code': error_status,
            'message': message
    }

    response = Response(json.dumps(data),
                        mimetype='application/json',
                        status=error_status)
    return response


def ok_response(message, additional_data=None):
    data = {
        'status': 'OK',
        'code': 200,
        'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
        'message': message,
    }
    if additional_data:
        for k, v in additional_data.items():
            data['{0}'.format(k)] = v
    response = Response(json.dumps(data),
                        mimetype='application/json',
                        status=200)
    return response


def ValidateRequestSchema(request, schema):
    try:
        result = schema.load(request.json)
    except Exception as ex:
        result = False
    if not result or (result and result.errors):
        return False
    return result


def create_random_uuid():
    return u'{0}'.format(uuid.uuid1())


def check_security_token_2(token, user):

    if not token == security_token(user.email, user.role.role_name, user.id, user.key_word):
        return False
    return True


def check_security_token(token):
    try:
        decode = jwt.decode(token, key_word, algorithms='HS256')
    except Exception as ex:
        print(ex)
        return False
    return decode


def security_token(username, role_name, user_id):
    signed = jwt.encode(
        {'userName': '{0}'.format(username),
         'role': '{0}'.format(role_name),
         'user_id': user_id
         }, key_word, algorithm='HS256')

    return signed


def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath


def check_passwords(password, confirm_password):
    if password != confirm_password:
        return False
    return True


def date_format(date, string=False, graph=False):
    if not string:
        return datetime.strftime(date, "%d.%m.%Y %H:%M:%S")
    date = date.split('T')
    if not graph:
        date = "{0} {1}".format(date[0], date[1].split('+')[0])
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return datetime.strftime(date, "%d.%m.%Y %H:%M:%S")
    date = "{0}".format(date[0])
    date = datetime.strptime(date, "%Y-%m-%d")
    return datetime.strftime(date, "%d-%b-%y")


def all_days_between_two_date(start_date, end_date):
    sdate = datetime.strptime(start_date, "%d-%b-%y")  # start date
    edate = datetime.strptime(end_date, "%d-%b-%y")  # end date
    delta = edate - sdate  # as timedelta
    days_list = []
    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        days_list.append(datetime.strftime(day, "%d-%b-%y"))
    return days_list
