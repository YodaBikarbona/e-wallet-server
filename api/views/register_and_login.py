from flask import jsonify
from flask_mail import Message
from api.helper.helper import (
    now,
    ValidateRequestSchema,
    error_handler,
    check_security_token,
    new_psw,
    security_token,
    random_string,
    ok_response,
    password_regex,
)
from api.model.config import mail, db
from config import session as Session
from api.model.user import User
from api.validation.register import RegisterSchema, LoginSchema
from api.model.providers.user import UserProvider
from api.messages import error_messages, messages
from api.validation.user import ActivationSchema
from api.helper.translations import _translation


def register(request):
    lang = request.headers['Lang']
    result = ValidateRequestSchema(request, RegisterSchema())
    if not result:
        return error_handler(error_status=400, message=_translation(original_string=error_messages.BAD_DATA,
                                                                    lang_code=lang))
    if request.json['password'] != request.json['confirmPassword']:
        return error_handler(error_status=400, message=_translation(original_string=error_messages.PASSWORDS_NOT_SAME,
                                                                    lang_code=lang))
    if not password_regex(request.json['password']):
        return error_handler(error_status=400, message=_translation(original_string=error_messages.PASSWORD_NOT_VALID,
                                                                    lang_code=lang))
    #check_user = UserProvider.get_user_by_email(request.json['email'])
    #check_user = User.query.filter(User.deleted != False, User.email == request.json['email']).first()
    if UserProvider.get_user_by_email(request.json['email']):
        #db.session.close()
        Session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.USER_ALREADY_EXISTS,
                                                                    lang_code=lang))
    user = UserProvider.create_register_user(request.json)
    if not user:
        Session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.REGEX_ERROR,
                                                                    lang_code=lang))
    return ok_response(message=messages.USER_CREATED)
    # code = user.code
    # recipient = request.json['email']
    # send_mail = send_code_to_mail(recipient=recipient, code=code)
    # if send_mail:
    #     Session.close()
    #     return ok_response(message=messages.USER_CREATED)
    # Session.close()
    # return error_handler(error_status=400, message='Something is wrong!')


def send_code_to_mail(recipient, code):
    msg = Message('Activation code', sender='privateewallet@gmail.com', recipients=['{0}'.format(recipient)])
    msg.body = 'Activation code: {0}'.format(code)
    try:
        mail.send(msg)
        return True
    except Exception as ex:
        return False


def login(request):
    lang = request.headers['Lang']
    if not ValidateRequestSchema(request, LoginSchema()):
        return error_handler(error_status=400, message=_translation(original_string=error_messages.BAD_DATA,
                                                                    lang_code=lang))
    user = UserProvider.get_user_by_email(request.json['email'])
    if not user:
        return error_handler(error_status=400, message=_translation(original_string=error_messages.WRONG_USERNAME_OR_PASSWORD,
                                                                    lang_code=lang))
    if user.password != new_psw(user.salt, request.json['password']):
        return error_handler(error_status=400, message=_translation(
            original_string=error_messages.WRONG_USERNAME_OR_PASSWORD,
            lang_code=lang))
    if not user.activated:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.USER_NOT_ACTIVATED,
                                                                    lang_code=lang))
    UserProvider.update_last_login(user_id=user.id)
    additional_data = {
        'user_id': user.id,
        'token': security_token(user.email, user.role.role_name, user.id),
    }
    return ok_response(message=messages.LOGIN, additional_data=additional_data)


def activate_user(request):
    lang = request.headers['Lang']
    if not ValidateRequestSchema(request, ActivationSchema()):
        return error_handler(error_status=400, message=_translation(original_string=error_messages.BAD_DATA,
                                                                    lang_code=lang))
    user = UserProvider.get_user_by_email(request.json['email'])
    if not user:
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.BAD_DATA,
                                                                    lang_code=lang))
    if user.code != request.json['code']:
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.INVALID_CODE,
                                                                    lang_code=lang))
    UserProvider.activate_user(user)
    #user.activated = True
    #user.code = ''
    #db.session.commit()
    return login(request)


def logout(request):
    lang = request.headers['Lang']
    #This function is no longer used (Frontend function is on now)
    user = UserProvider.get_user_by_ID(request.json['user_id'])
    if not user:
        return error_handler(error_status=400, message=_translation(original_string=error_messages.BAD_DATA,
                                                                    lang_code=lang))
    if not check_security_token(token=request.headers['Authorization'], user=user):
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    UserProvider.update_key_word(user)
    return ok_response(message=messages.LOGOUT)

