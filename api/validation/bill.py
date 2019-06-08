from marshmallow import Schema, fields, post_load


class New_Bill(object):
    def __init__(self, title, price, user_id, currency_id):
        self.title = title
        self.price = price
        self.user_id = user_id
        self.currency_id = currency_id


class NewBillSchema(Schema):
    title = fields.String()
    price = fields.Float()
    user_id = fields.Integer()
    currency_id = fields.Integer()

    @post_load
    def _activation(self, data):
        return New_Bill(**data)
