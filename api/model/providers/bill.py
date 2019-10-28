from api.model.bill import Bill, BillCategory, BillSubCategory
from api.model.country import Currency
from api.model.config import db
from config import session as Session
from api.model.bill import UserBillSubCategory


class BillProvider:

    # Need remove all db.session.remove() parts, sesion cannot be closed in different scope
    # Need remove all db.session.add or .commit with Session()

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
        # db.session.add(new_bill)
        # db.session.commit()
        # db.session.close()
        Session.add(new_bill)
        Session.commit()
        return new_bill

    @classmethod
    def get_categories(cls):
        categories = Session.query(BillCategory)\
            .filter()
        return categories.all()

    @classmethod
    def get_sub_categories(cls, category_id, user_id):
        if category_id == 'null':
            category_id = None
        user_subcategories = Session.query(UserBillSubCategory).filter(UserBillSubCategory.user_id == user_id).all()
        if user_subcategories:
            user_subcategories = [user_sub.bill_sub_category_id for user_sub in user_subcategories]
        else:
            return []
        sub_categories = Session.query(BillSubCategory)\
            .filter(BillSubCategory.bill_category_id == category_id,
                    BillSubCategory.id.in_(user_subcategories))
        return sub_categories.all()

    @classmethod
    def get_currencies(cls):
        currencies = Session.query(Currency).filter()
        return currencies.all()

    @classmethod
    def get_costs_or_profits(cls, category_id, sub_category_id, currency_id, user_id, bill_type, bills_limit=None, bills_offset=None, search=None):
        bills = Session.query(Bill)\
            .filter(Bill.user_id == user_id)
        if category_id and category_id != 'null':
            bills = bills.join(BillCategory, Bill.bill_category_id == BillCategory.id)
            bills = bills.filter(Bill.bill_category_id == category_id)
        if sub_category_id and sub_category_id != 'null':
            bills = bills.join(BillSubCategory, Bill.bill_sub_category_id == BillSubCategory.id)
            bills = bills.filter(Bill.bill_sub_category_id == sub_category_id)
        if currency_id and currency_id != 'null':
            bills = bills.join(Currency, Bill.currency_id == Currency.id)
            bills = bills.filter(Bill.currency_id == currency_id)
        if search:
            bills = bills.filter(Bill.title.ilike('%{0}%'.format(search)))
        bills = bills.filter(Bill.bill_type == bill_type)
        bills = bills.order_by(Bill.created.desc())
        if bills_limit:
            bills = bills.limit(bills_limit)
        if bills_offset:
            bills = bills.offset(bills_offset*bills_limit)

        return bills.all()

    @classmethod
    def count_costs_or_profits(cls, category_id, sub_category_id, currency_id, user_id, bill_type, search):
        return len(cls.get_costs_or_profits(
            category_id=category_id,
            sub_category_id=sub_category_id,
            currency_id=currency_id,
            user_id=user_id,
            bill_type=bill_type,
            search=search
        ))

    @classmethod
    def new_costs_or_profits(cls, category_id, sub_category_id, currency_id, title, comment, price, user_id, bill_type, quantity, not_my_city, image_id=None):
        new_bill = Bill()
        new_bill.user_id = user_id
        new_bill.title = title
        new_bill.price = float(price)
        new_bill.currency_id = currency_id
        new_bill.comment = comment
        new_bill.image_id = image_id if image_id else None
        new_bill.bill_category_id = category_id
        new_bill.bill_sub_category_id = sub_category_id if sub_category_id and sub_category_id != 'null' else None
        new_bill.bill_type = bill_type
        new_bill.quantity = quantity
        new_bill.not_my_city = not_my_city
        # db.session.add(new_bill)
        # db.session.commit()
        # db.session.close()
        Session.add(new_bill)
        Session.commit()
        #Session.close()
        return True

    @classmethod
    def get_subcategory_by_sub_cat_id(cls, bill_sub_category_id):
        subcategory = Session.query(BillSubCategory)\
            .filter(BillSubCategory.id == bill_sub_category_id)
        return subcategory.first()

    @classmethod
    def get_all_costs_and_profits(cls, costs, profits, user_id, currency_id):
        bills = Session.query(Bill)\
            .filter(Bill.user_id == user_id,
                    Bill.currency_id == currency_id)
        if costs and not profits:
            bills = bills.filter(Bill.bill_type == 'costs')
        if profits and not costs:
            bills = bills.filter(Bill.bill_type == 'profits')
        return bills.all()

    @classmethod
    def delete_bill_by_bill_id(cls, bill_id):
        bill = Session.query(Bill)\
            .filter(Bill.id == bill_id)\
            .first()
        # db.session.delete(bill)
        # db.session.commit()
        # db.session.close()
        Session.delete(bill)
        Session.commit()
        #Session.close()
        return True
