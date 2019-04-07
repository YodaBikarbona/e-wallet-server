from marshmallow import Schema, fields, post_load


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
