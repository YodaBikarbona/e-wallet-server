from marshmallow import Schema, fields, post_load
from enum import Enum
from marshmallow_enum import EnumField


class Register(object):
    def __init__(self, address, birthDate, city, confirmPassword, email, firstName, gender, lastName, password, state):
        self.address = address
        self.birthDate = birthDate
        self.city = city
        self.confirmPassword = confirmPassword
        self.email = email
        self.firstName = firstName
        self.gender = gender
        self.lastName = lastName
        self.password = password
        self.state = state


class Login(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password


class Gender(Enum):
    male = "m"
    female = "f"


class RegisterSchema(Schema):
    address = fields.String()
    birthDate = fields.Date()
    city = fields.String()
    confirmPassword = fields.String()
    email = fields.Email()
    firstName = fields.String()
    gender = EnumField(Gender)
    lastName = fields.String()
    password = fields.String()
    state = fields.String()

    @post_load
    def get_register(self, data):
        return Register(**data)


class LoginSchema(Schema):
    email = fields.Email()
    password = fields.String()

    @post_load
    def _login(self, data):
        return Login(**data)
