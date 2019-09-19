from api.model.bill import Bill, BillCategory, BillSubCategory
from api.model.country import Currency
from api.model.config import db


class BillProvider:


    @classmethod
    def add_new_bill(cls, bill_data):
        new_bill = Bill()
        new_bill.user_id = bill_data['user_id']
        new_bill.title = bill_data['title']
        new_bill.price = bill_data['price']
        new_bill.currency_id = bill_data['currency_id']
        new_bill.comment = bill_data['comment']
        new_bill.image_id = bill_data['image_id'] if 'image_id' in bill_data else None
        new_bill.bill_category_id = bill_data['bill_category_id'] if 'bill_category_id' in bill_data else None
        new_bill.bill_sub_category_id = bill_data['bill_sub_category_id'] if 'bill_sub_category_id' in bill_data else None
        db.session.add(new_bill)
        db.session.commit()
        return new_bill

    @classmethod
    def get_categories(cls):
        categories = BillCategory.query.filter().all()

        return categories

    @classmethod
    def get_sub_categories(cls, category_id):
        sub_categories = BillSubCategory.query.filter(BillSubCategory.bill_category_id == category_id).all()

        return sub_categories

    @classmethod
    def get_currencies(cls):
        currencies = Currency.query.filter().all()

        return currencies

    @classmethod
    def get_costs_or_profits(cls, category_id, sub_category_id, currency_id, user_id, bill_type):
        bills = Bill.query.filter(Bill.user_id == user_id)
        if category_id and category_id != 'null':
            bills = bills.join(BillCategory, Bill.bill_category_id == BillCategory.id)
            bills = bills.filter(Bill.bill_category_id == category_id)
        if sub_category_id and sub_category_id != 'null':
            bills = bills.join(BillSubCategory, Bill.bill_sub_category_id == BillSubCategory.id,)
            bills = bills.filter(Bill.bill_sub_category_id == sub_category_id)
        if currency_id and currency_id != 'null':
            bills = bills.join(Currency, Bill.currency_id == Currency.id)
            bills = bills.filter(Bill.currency_id == currency_id)
        bills = bills.filter(Bill.bill_type == bill_type)
        return bills.all()

    @classmethod
    def new_costs_or_profits(cls, category_id, sub_category_id, currency_id, title, comment, price, user_id, bill_type, image_id=None):
        new_bill = Bill()
        new_bill.user_id = user_id
        new_bill.title = title
        new_bill.price = float(price)
        new_bill.currency_id = currency_id
        new_bill.comment = comment
        new_bill.image_id = image_id if image_id else None
        new_bill.bill_category_id = category_id
        new_bill.bill_sub_category_id = sub_category_id
        new_bill.bill_type = bill_type
        db.session.add(new_bill)
        db.session.commit()
        return True

    @classmethod
    def get_subcategory_by_sub_cat_id(cls, bill_sub_category_id):
        return BillSubCategory.query.filter(BillSubCategory.id == bill_sub_category_id).first()
