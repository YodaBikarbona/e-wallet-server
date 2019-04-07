from datetime import datetime
from api.helper.helper import new_salt, new_psw, random_string
from api.model.config import db
from api.model.user import User, Role


class UserProvider:

    @classmethod
    def create_register_user(cls, user_data):
        role = Role.query.filter(Role.role_name == 'user').first()
        user = User()
        user.gender = user_data['gender']
        user.email = user_data['email']
        user.city = u'{0}'.format(user_data['city'])
        user.address = u'{0}'.format(user_data['address'])
        user.birth_date = datetime.strptime(user_data['birthDate'], "%d/%m/%Y").strftime("%Y-%m-%d")
        user.first_name = u'{0}'.format(user_data['firstName'])
        user.last_name = u'{0}'.format(user_data['lastName'])
        user.state = u'{0}'.format(user_data['state'])
        user.key_word = random_string(255)
        user.code = random_string(6)
        user.salt = new_salt()
        user.password = new_psw(user.salt, user_data['password'])
        user.role_id = role.id
        user.image_id = 1
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_user_by_ID(cls, user_id):
        user = User.query.filter(User.id == user_id).first()
        return user

    @classmethod
    def get_user_by_email(cls, email):
        user = User.query.filter(User.email == email).first()
        return user

    @classmethod
    def activate_user(cls, user):
        user.code = ''
        user.activated = True
        db.session.commit()
        return True

    @classmethod
    def update_key_word(cls, user):
        user.key_word = random_string(255)
        db.session.commit()
        return True
