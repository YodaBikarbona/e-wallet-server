from datetime import datetime
from hashlib import sha512
from random import choice
from jose import jwt
import json
import logging
from datetime import datetime
from flask import Response
import os
import uuid
import string
import random

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


def check_security_token(token, user):

    if not token == security_token(user.email, user.role.role_name, user.id, user.key_word):
        return False
    return True


def decode_security_token(token, user):
    try:
        decode = jwt.decode(token, user.key_word, algorithms='HS256')
    except Exception as ex:
        print(ex)
        return False
    return decode


def security_token(username, role_name, user_id, key_word):
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
