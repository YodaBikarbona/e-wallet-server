from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField
from api.validation.register import Gender


class Activation(object):
    def __init__(self, email, password, code):
        self.email = email
        self.password = password
        self.code = code


class ActivationSchema(Schema):
    email = fields.Email()
    password = fields.String()
    code = fields.String()

    @post_load
    def _activation(self, data):
        return Activation(**data)


class EditUser(object):
    def __init__(self, firstName, lastName, country_id, city_id, address, email, phone, gender, currency_id):
        self.firstName = firstName
        self.lastName = lastName
        #self.birthDate = birthDate
        self.country_id = country_id
        self.city_id = city_id
        self.address = address
        self.email = email
        self.phone = phone
        self.gender = gender
        self.currency_id = currency_id


class EditUserSchema(Schema):
    firstName = fields.String()
    lastName = fields.String()
    #birthDate = fields.String()
    country_id = fields.Integer()
    city_id = fields.Integer()
    address = fields.String()
    email = fields.String()
    phone = fields.String()
    gender = EnumField(Gender)
    currency_id = fields.String()

    @post_load()
    def _edit_user(self, data):
        return EditUser(**data)
