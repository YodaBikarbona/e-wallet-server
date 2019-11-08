from marshmallow import Schema, fields, post_load
from enum import Enum
from marshmallow_enum import EnumField


class Register(object):
    def __init__(self, address, birthDate, city_id, confirmPassword, email, firstName, gender, lastName, password, country_id):
        self.address = address
        self.birthDate = birthDate
        self.city_id = city_id
        self.confirmPassword = confirmPassword
        self.email = email
        self.firstName = firstName
        self.gender = gender
        self.lastName = lastName
        self.password = password
        self.country_id = country_id


class Login(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password


class Gender(Enum):
    Male = "m"
    Female = "f"


class RegisterSchema(Schema):
    address = fields.String()
    birthDate = fields.String()
    city_id = fields.Integer()
    confirmPassword = fields.String()
    email = fields.Email()
    firstName = fields.String()
    gender = EnumField(Gender)
    lastName = fields.String()
    password = fields.String()
    country_id = fields.Integer()

    @post_load
    def get_register(self, data):
        return Register(**data)


class LoginSchema(Schema):
    email = fields.Email()
    password = fields.String()

    @post_load
    def _login(self, data):
        return Login(**data)
