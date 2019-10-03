from datetime import datetime
import datetime as dt
from api.helper.helper import new_salt, new_psw, random_string, now
from api.model.config import db
from api.model.user import User, Role, UserCurrency
from api.model.bill import Currency, UserBillCategory, UserBillSubCategory, BillCategory, BillSubCategory


class UserProvider:

    @classmethod
    def create_register_user(cls, user_data):
        role = Role.query.filter().all()
        if len(role) == 0:
            role = UserProvider.create_role(role_name='admin')
        elif len(role) == 1 and not [r for r in role if r.role_name == 'user']:
            role = UserProvider.create_role(role_name='user')
        else:
            role = Role.query.filter(Role.role_name == 'user').first()
        user = User()
        user.gender = user_data['gender']
        user.email = user_data['email']
        user.city_id = u'{0}'.format(user_data['city_id'])
        user.address = u'{0}'.format(user_data['address'])
        user.birth_date = datetime.strptime(user_data['birthDate'], "%Y-%m-%d")#.strftime("%Y-%m-%d")
        user.first_name = u'{0}'.format(user_data['firstName'])
        user.last_name = u'{0}'.format(user_data['lastName'])
        user.country_id = u'{0}'.format(user_data['country_id'])
        user.key_word = random_string(255)
        user.code = random_string(6)
        user.salt = new_salt()
        user.password = new_psw(user.salt, user_data['password'])
        user.role_id = role.id
        user.image_id = None
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

    @classmethod
    def get_all_users(cls, user_id, filters=None):
        users = User.query.filter(User.id != user_id).all()

        return users

    @classmethod
    def create_role(cls, role_name):
        new_role = Role()
        new_role.role_name = role_name
        db.session.add(new_role)
        db.session.commit()
        return new_role

    @classmethod
    def set_new_restart_code(cls, user, code=False):
        if code:
            user.code = random_string(6)
        else:
            user.new_password_code = random_string(6)
            user.new_password_code_expired = now() + dt.timedelta(minutes=5)
        db.session.commit()
        return True

    @classmethod
    def check_expired_restart_code(cls, user, user_data):
        return (user.new_password_code_expired > now() or user.new_password_code != user_data['code'])

    @classmethod
    def save_new_password(cls, user, user_data):
        user.salt = new_salt()
        user.password = new_psw(user.salt, user_data['newPassword'])
        user.activated = False
        db.session.commit()
        return True

    @classmethod
    def user_settings_currencies(cls, active, user_id, search):
        if not active:
            user_currencies = UserCurrency.query.filter(UserCurrency.user_id == user_id).all()
            currencies_ids = [curr.currency_id for curr in user_currencies] if user_currencies else []
            bill_currencies = Currency.query.filter(Currency.id.notin_(currencies_ids))
        else:
            bill_currencies = Currency.query\
                .join(UserCurrency, Currency.id == UserCurrency.currency_id)\
                .filter(UserCurrency.user_id == user_id)
        if search:
            bill_currencies = bill_currencies.filter(Currency.code.ilike('%{0}%'.format(search)))
        return bill_currencies.all()

    @classmethod
    def check_user_currencies_number(cls, user_id):
        currencies_number = UserCurrency.query.filter(UserCurrency.user_id == user_id).count()
        return currencies_number

    @classmethod
    def check_user_categories_number(cls, user_id):
        categories_number = UserBillCategory.query.filter(UserBillCategory.user_id == user_id).count()
        return categories_number

    @classmethod
    def check_user_sub_categories_number(cls, user_id):
        sub_categories_number = UserBillSubCategory.query.filter(UserBillSubCategory.user_id == user_id).count()
        return sub_categories_number

    @classmethod
    def save_or_delete_user_settings_currency(cls, active, currency_id, user_id):
        if not active:
            new_currency = UserCurrency()
            new_currency.user_id = user_id
            new_currency.currency_id = currency_id
            db.session.add(new_currency)
            db.session.commit()
            return True
        else:
            user_currency = UserCurrency.query.filter(UserCurrency.user_id == user_id,
                                                      UserCurrency.currency_id == currency_id).first()
            if user_currency:
                db.session.delete(user_currency)
                db.session.commit()
            return True

    @classmethod
    def user_settings_categories(cls, active, user_id, search):
        if not active:
            user_categories = UserBillCategory.query.filter(UserBillCategory.user_id == user_id).all()
            categories_ids = [cat.bill_category_id for cat in user_categories] if user_categories else []
            bill_categories = BillCategory.query.filter(BillCategory.id.notin_(categories_ids))
        else:
            bill_categories = BillCategory.query.join(UserBillCategory, BillCategory.id == UserBillCategory.bill_category_id). \
                filter(UserBillCategory.user_id == user_id)
        if search:
            bill_categories = bill_categories.filter(BillCategory.name.ilike('%{0}%'.format(search)))
        return bill_categories.all()

    @classmethod
    def user_settings_sub_categories(cls, active, user_id, search):
        # Get all active user categories
        user_categories = cls.user_settings_categories(active=True, user_id=user_id, search='')
        # Get all subcategories of active categories
        sub_cats = BillSubCategory.query.filter(
            BillSubCategory.bill_category_id.in_([cat.id for cat in user_categories])
        ).all() if user_categories else []
        if not active:
            # Get all active subcategories
            user_sub_categories = UserBillSubCategory.query.filter(
                UserBillSubCategory.user_id == user_id,
                UserBillSubCategory.bill_sub_category_id.in_([sub.id for sub in sub_cats])
            ).all() if sub_cats else []
            # If not active subcategories for active categories return all subcategories for active categories
            if not user_sub_categories:
                return sub_cats
            # If active subcategories exist than return inactive subcategories of active categories
            sub_categories_ids = [sub_cat.bill_sub_category_id for sub_cat in
                                  user_sub_categories] if user_sub_categories else []
            sub_categories_ids_filter = [sub.id for sub in sub_cats if
                                         sub.id not in sub_categories_ids] if sub_categories_ids else []
            bill_sub_categories = BillSubCategory.query.filter(
                BillSubCategory.id.in_(sub_categories_ids_filter))
            if not sub_categories_ids_filter:
                return []
        else:
            bill_sub_categories = BillSubCategory.query\
                .join(UserBillSubCategory, BillSubCategory.id == UserBillSubCategory.bill_sub_category_id)\
                .filter(UserBillSubCategory.user_id == user_id,
                        UserBillSubCategory.bill_sub_category_id.in_([sub.id for sub in sub_cats]))
        if search:
            bill_sub_categories = bill_sub_categories.filter(BillSubCategory.name.ilike('%{0}%'.format(search)))
        return bill_sub_categories.all()

    @classmethod
    def save_or_delete_user_settings_category(cls, active, category_id, user_id):
        if not active:
            new_category = UserBillCategory()
            new_category.user_id = user_id
            new_category.bill_category_id = category_id
            db.session.add(new_category)
            db.session.commit()
            return True
        else:
            user_category = UserBillCategory.query.filter(UserBillCategory.user_id == user_id,
                                                          UserBillCategory.bill_category_id == category_id).first()
            user_sub_categories = UserBillSubCategory.query \
                .join(BillSubCategory, UserBillSubCategory.bill_sub_category_id == BillSubCategory.id) \
                .filter(BillSubCategory.id == category_id).all()
            if user_category:
                db.session.delete(user_category)
                db.session.commit()
            if user_sub_categories:
                for sub_category in user_sub_categories:
                    db.session.delete(sub_category)
                    db.session.commit()
            return True

    @classmethod
    def save_or_delete_user_settings_sub_category(cls, active, sub_category_id, user_id):
        if not active:
            new_sub_category = UserBillSubCategory()
            new_sub_category.user_id = user_id
            new_sub_category.bill_sub_category_id = sub_category_id
            db.session.add(new_sub_category)
            db.session.commit()
            return True
        else:
            user_sub_category = UserBillSubCategory.query\
                .filter(UserBillSubCategory.user_id == user_id,
                        UserBillSubCategory.bill_sub_category_id == sub_category_id).first()
            if user_sub_category:
                db.session.delete(user_sub_category)
                db.session.commit()
            return True

    @classmethod
    def edit_user(cls, user_data, user_email, user_id):
        # First check new user email
        if cls.get_user_by_email(email=user_data['email']) and user_email != user_data['email']:
            return False
        user = cls.get_user_by_ID(user_id == user_id)
        user.gender = user_data['gender']
        user.email = user_data['email']
        user.city_id = u'{0}'.format(user_data['city_id'])
        user.address = u'{0}'.format(user_data['address'])
        user.birth_date = datetime.strptime(user_data['birthDate'], "%Y-%m-%d")  # .strftime("%Y-%m-%d")
        user.first_name = u'{0}'.format(user_data['firstName'])
        user.last_name = u'{0}'.format(user_data['lastName'])
        user.country_id = u'{0}'.format(user_data['country_id'])
        user.phone = u'{0}'.format(user_data['phone'])
        user.currency_id = u'{0}'.format(user_data['currency_id']) if user_data['currency_id'] != 'null' else None
        db.session.commit()
        return True

    @classmethod
    def get_active_user_currencies_with_limit(cls, user_id):
        return UserCurrency.query.filter(UserCurrency.user_id == user_id).all()

    @classmethod
    def edit_active_user_currencies_with_limit(cls, currency_id, monthly_limit):
        currency = UserCurrency.query.filter(UserCurrency.id == currency_id).first()
        currency.monthly_cost_limit = monthly_limit
        db.session.commit()
        return True

    @classmethod
    def get_user_currency_by_currency_id(cls, currency_id):
        return UserCurrency.query\
            .join(Currency, UserCurrency.currency_id == Currency.id)\
            .filter(Currency.id == currency_id).first()
