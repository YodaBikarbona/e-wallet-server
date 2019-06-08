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
    def get_costs(cls, category_id, sub_category_id, currency_id, user_id):
        bills = Bill.query.filter(Bill.user_id == user_id)
        if category_id:
            bills = bills.join(BillCategory, Bill.bill_category_id == BillCategory.id)
            bills = bills.filter(Bill.bill_category_id == category_id)
        if sub_category_id:
            bills = bills.join(BillSubCategory, Bill.bill_sub_category_id == BillSubCategory.id,)
            bills = bills.filter(Bill.bill_sub_category_id == sub_category_id)
        if currency_id:
            bills = bills.join(Currency, Bill.currency_id == Currency.id)
            bills = bills.filter(Bill.currency_id == currency_id)
        return bills.all()
