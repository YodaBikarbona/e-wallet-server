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
from api.model.user import User
from api.validation.register import RegisterSchema, LoginSchema
from api.model.providers.user import UserProvider
from api.messages import error_messages, messages
from api.validation.user import ActivationSchema


def register(request):

    print(request.json)
    result = ValidateRequestSchema(request, RegisterSchema())
    if not result:
        return error_handler(400, error_messages.BAD_DATA)
    if request.json['password'] != request.json['confirmPassword']:
        return error_handler(400, error_messages.PASSWORDS_NOT_SAME)
    if not password_regex(request.json['password']):
        return error_handler(400, error_messages.PASSWORD_NOT_VALID)
    #check_user = UserProvider.get_user_by_email(request.json['email'])
    #check_user = User.query.filter(User.deleted != False, User.email == request.json['email']).first()
    if UserProvider.get_user_by_email(request.json['email']):
        db.session.close()
        return error_handler(400, error_messages.USER_ALREADY_EXISTS)
    user = UserProvider.create_register_user(request.json)
    code = user.code
    recipient = request.json['email']
    send_mail = send_code_to_mail(recipient=recipient, code=code)
    if send_mail:
        db.session.close()
        return ok_response(messages.USER_CREATED)
        """return jsonify(
            {
                'status': 'OK',
                'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
                'code': 200,
                'msg': "User is successfully created!"
            }
        )"""
    db.session.close()
    return error_handler(400, 'Something is wrong!')


def send_code_to_mail(recipient, code):
    msg = Message('Activation code', sender='privateewallet@gmail.com', recipients=['{0}'.format(recipient)])
    msg.body = 'Activation code: {0}'.format(code)
    try:
        mail.send(msg)
        return True
    except Exception as ex:
        return False


def login(request):
    if not ValidateRequestSchema(request, LoginSchema()):
        return error_handler(400, error_messages.BAD_DATA)
    user = UserProvider.get_user_by_email(request.json['email'])
    if not user:
        db.session.close()
        return error_handler(400, error_messages.USER_NOT_EXISTS)
    if user.password != new_psw(user.salt, request.json['password']):
        db.session.close()
        return error_handler(400, error_messages.WRONG_USERNAME_OR_PASSWORD)
    if not user.activated:
        db.session.close()
        return error_handler(403, error_messages.USER_NOT_ACTIVATED)
    user.last_login = now()
    db.session.commit()
    additional_data = {
        'user_id': user.id,
        'token': security_token(user.email, user.role.role_name, user.id),
    }
    print("This is role id", user.role_id)
    db.session.close()
    return ok_response(messages.LOGIN, additional_data)


def activate_user(request):
    if not ValidateRequestSchema(request, ActivationSchema()):
        return error_handler(400, error_messages.BAD_DATA)
    user = UserProvider.get_user_by_email(request.json['email'])
    if not user:
        db.session.close()
        return error_handler(400, error_messages.BAD_DATA)
    if user.code != request.json['code']:
        db.session.close()
        return error_handler(400, error_messages.INVALID_CODE)
    UserProvider.activate_user(user)
    #user.activated = True
    #user.code = ''
    #db.session.commit()
    return login(request)


def logout(request):

    user = UserProvider.get_user_by_ID(request.json['user_id'])
    if not user:
        return error_handler(400, error_messages.BAD_DATA)
    if not check_security_token(token=request.headers['Authorization'], user=user):
        return error_handler(403, error_messages.INVALID_TOKEN)
    UserProvider.update_key_word(user)
    return ok_response(messages.LOGOUT)

