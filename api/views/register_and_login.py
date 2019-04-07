from flask import jsonify
from flask_mail import Message
from api.helper.helper import now, ValidateRequestSchema, error_handler, check_security_token, new_psw, security_token, random_string
from api.model.config import mail, db
from api.model.user import User
from api.validation.register import RegisterSchema
from api.model.providers.user import UserProvider
from api.messages import error_messages


def register(request):

    result = ValidateRequestSchema(request, RegisterSchema())
    if not result:
        return error_handler(400, error_messages.BAD_DATA)
    if request.json['password'] != request.json['confirmPassword']:
        return error_handler(400, error_messages.PASSWORDS_NOT_SAME)

    check_user = User.query.filter(User.deleted != False, User.email == request.json['email']).first()
    if check_user:
        return error_handler(400, 'User with that email already exists!')
    user = UserProvider.create_register_user(request.json)
    code = user.code
    recipient = request.json['email']
    send_mail = send_code_to_mail(recipient=recipient, code=code)
    if send_mail:
        return jsonify(
            {
                'status': 'OK',
                'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
                'code': 200,
                'msg': "User is successfully created!"
            }
        )
    return error_handler(400, 'Something is wrong!')

def send_code_to_mail(recipient, code):
    msg = Message('Activation code', sender='michael.p.b.6@gmail.com', recipients=['{0}'.format(recipient)])
    msg.body = 'Activation code: {0}'.format(code)
    try:
        mail.send(msg)
        return True
    except Exception as ex:
        return False


def login(request):
    if "password" not in request.json or "email" not in request.json:
        return error_handler(400, 'Something is wrong!')
    if request.json['password'] and request.json['email']:
        user = User.query.filter(User.email == request.json['email']).first()
        if not user:
            return error_handler(400, 'Something is wrong!')
        check_password = new_psw(user.salt, request.json['password'])
        if check_password != user.password:
            return error_handler(400, 'Password is wrong!')
        if not user.activated:
            return error_handler(403, 'User is not activated!')
        user.last_login = now()
        db.session.commit()
        return jsonify(
            {
                'status': 'OK',
                'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
                'code': 200,
                #'user': UsersSerializer(many=False).dump(user).data,
                'user_id': user.id,
                'msg': 'You are successfully logged in',
                'token': security_token(user.email, user.role.role_name, user.id, user.key_word)
            }
        )


def activate_user(request):
    if request.json['password'] and request.json['email'] and request.json['code']:
        user = User.query.filter(User.email == request.json['email']).first()
        if not user:
            return error_handler(400, 'Something is wrong!')
    if user.code != request.json['code']:
        return error_handler(400, "Code is not valid!")
    user.activated = True
    user.code = ''
    db.session.commit()
    return login(request)

def logout_user(request):

    user = User.query.filter(User.id == request.json['user_id']).first()
    if not user:
        return error_handler(400, 'Something is wrong!')
    if not check_security_token(token=request.headers['Authorization'], user=user):
        return error_handler(403, "Token is wrong!")
    user = User.query.filter(User.id == request.json['user_id']).first()
    user.key_word = random_string(255)
    db.session.commit()
    return jsonify(
            {
                'status': 'OK',
                'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
                'code': 200,
                #'user': UsersSerializer(many=False).dump(user).data,
                'msg': 'You are successfully logged out!',
            }
        )
