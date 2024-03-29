from datetime import datetime
import datetime as dt
from api.helper.helper import (
    new_salt,
    new_psw,
    random_string,
    now,
    regex,
)
from api.model.config import db
from api.model.user import (
    User,
    Role,
    UserCurrency,
    News,
    UserNews,
)
from api.model.bill import (
    Currency,
    UserBillCategory,
    UserBillSubCategory,
    BillCategory,
    BillSubCategory,
    TranslationBillCategory,
    TranslationBillSubCategory
)
from api.helper.helper import date_format
from config import session as Session
from api.model.providers.bill import BillProvider


class UserProvider:

    #Need remove all db.session.remove() parts, sesion cannot be closed in different scope
    #Need remove all db.session.add or .commit with Session()

    @classmethod
    def create_register_user(cls, user_data):
        role = Session.query(Role).filter().all()
        if len(role) == 0:
            role = UserProvider.create_role(role_name='admin')
        elif len(role) == 1 and not [r for r in role if r.role_name == 'user']:
            role = UserProvider.create_role(role_name='user')
        else:
            role = Session.query(Role).filter(Role.role_name == 'user').first()
        print(user_data['birthDate'])
        try:
            user = User()
            user.gender = user_data['gender']
            user.email = user_data['email'] if regex(regex_string=user_data['email'],
                                                     email=True) else None
            user.city_id = u'{0}'.format(user_data['city_id'])
            user.address = u'{0}'.format(user_data['address'])
            user.birth_date = datetime.strptime(date_format(user_data['birthDate'], string=True, graph=False, birth_day=True, register=True), "%Y-%m-%d")#.strftime("%Y-%m-%d")
            user.first_name = u'{0}'.format(user_data['firstName']) if regex(regex_string=user_data['firstName'],
                                                                             first_name=True) else None
            user.last_name = u'{0}'.format(user_data['lastName']) if regex(regex_string=user_data['lastName'],
                                                                           last_name=True) else None
            user.country_id = u'{0}'.format(user_data['country_id'])
            user.key_word = random_string(255)
            user.code = random_string(6)
            user.salt = new_salt()
            user.password = new_psw(user.salt, user_data['password'])
            user.role_id = role.id
            user.activated = True
            #user.image_id = None
            #user.image_id = 1 if user_data['gender'] == 'male' else user.image_id
            #user.image_id = 2 if user_data['gender'] == 'female' else user.image_id
            Session.add(user)
            Session.commit()
            #db.session.add(user)
            #db.session.commit()
        except Exception as ex:
            Session.rollback()
            print(ex)
            return False
        return user

    @classmethod
    def get_user_by_ID(cls, user_id):
        user = Session.query(User).filter(User.id == user_id).first()
        return user

    @classmethod
    def get_user_by_email(cls, email):
        if not regex(regex_string=email, email=True):
            return None
        user = Session.query(User).filter(User.email == email).first()
        return user

    @classmethod
    def update_last_login(cls, user_id):
        user = Session.query(User).filter(User.id == user_id).first()
        user.last_login = now()
        #db.session.commit()
        Session.commit()
        #Session.close()
        return True

    @classmethod
    def activate_user(cls, user):
        user.code = ''
        user.activated = True
        #db.session.commit()
        #db.session.close()
        Session.commit()
        return True

    @classmethod
    def update_key_word(cls, user):
        user.key_word = random_string(255)
        #db.session.commit()
        #db.session.close()
        #Session.close()
        return True

    @classmethod
    def get_all_users(cls, user_id, filters=None):
        users = Session.query(User).filter(User.id != user_id).all()
        return users

    @classmethod
    def create_role(cls, role_name):
        new_role = Role()
        new_role.role_name = role_name
        #db.session.add(new_role)
        #db.session.commit()
        #db.session.close()
        Session.add(new_role)
        Session.commit()
        return new_role

    @classmethod
    def set_new_restart_code(cls, user, code=False):
        if code:
            user.code = random_string(6)
        else:
            user.new_password_code = random_string(6)
            user.new_password_code_expired = now() + dt.timedelta(minutes=5)
        #db.session.commit()
        #db.session.close()
        Session.commit()
        return True

    @classmethod
    def set_new_login_code(cls, user):
        user.code = random_string(6)
        # db.session.commit()
        # db.session.close()
        Session.commit()
        return True

    @classmethod
    def check_expired_restart_code(cls, user, user_data):
        return (user.new_password_code_expired > now() or user.new_password_code != user_data['code'])

    @classmethod
    def save_new_password(cls, user, user_data):
        user.salt = new_salt()
        user.password = new_psw(user.salt, user_data['newPassword'])
        # user.activated = False
        # db.session.commit()
        # db.session.close()
        Session.commit()
        return True

    @classmethod
    def user_settings_currencies(cls, active, user_id, search):
        if not active:
            user_currencies = Session.query(UserCurrency).filter(UserCurrency.user_id == user_id).all()
            currencies_ids = [curr.currency_id for curr in user_currencies] if user_currencies else []
            #Session.close()
            bill_currencies = Session.query(Currency).filter(Currency.id.notin_(currencies_ids))
        else:
            bill_currencies = Session.query(Currency)\
                .join(UserCurrency, Currency.id == UserCurrency.currency_id)\
                .filter(UserCurrency.user_id == user_id)
        if search:
            bill_currencies = bill_currencies.filter(Currency.code.ilike('%{0}%'.format(search)))
        return bill_currencies.all()

    @classmethod
    def check_user_currencies_number(cls, user_id):
        currencies_number = Session.query(UserCurrency).filter(UserCurrency.user_id == user_id).count()
        #db.session.close()
        #Session.close()
        return currencies_number

    @classmethod
    def check_user_categories_number(cls, user_id):
        categories_number = Session.query(UserBillCategory)\
            .filter(UserBillCategory.user_id == user_id)\
            .count()
        #Session.close()
        return categories_number

    @classmethod
    def check_user_sub_categories_number(cls, user_id):
        sub_categories_number = Session.query(UserBillSubCategory)\
            .filter(UserBillSubCategory.user_id == user_id)\
            .count()
        #Session.close()
        return sub_categories_number

    @classmethod
    def save_or_delete_user_settings_currency(cls, active, currency_id, user_id):
        costs = len(BillProvider.get_costs_or_profits(
            category_id=None, sub_category_id=None, currency_id=currency_id,
            user_id=user_id, bill_type='costs', bills_limit=None,
            bills_offset=None))
        profits = len(BillProvider.get_costs_or_profits(
            category_id=None, sub_category_id=None, currency_id=currency_id,
            user_id=user_id, bill_type='profits', bills_limit=None,
            bills_offset=None))
        if not active:
            new_currency = UserCurrency()
            new_currency.user_id = user_id
            new_currency.currency_id = currency_id
            # db.session.add(new_currency)
            # db.session.commit()
            # db.session.close()
            Session.add(new_currency)
            Session.commit()
            #Session.close()
            return True
        else:
            if costs or profits:
                return False
            user_currency = Session.query(UserCurrency)\
                .filter(UserCurrency.user_id == user_id,
                        UserCurrency.currency_id == currency_id)\
                .first()
            if user_currency:
                user = cls.get_user_by_ID(user_id=user_id)
                if user.currency_id == currency_id:
                    user.currency_id = None
                # db.session.delete(user_currency)
                # db.session.commit()
                Session.delete(user_currency)
                Session.commit()
            #Session.close()
            return True

    @classmethod
    def user_settings_categories(cls, active, user_id, search, lang_code='en'):
        if not active:
            user_categories = Session.query(UserBillCategory)\
                .filter(UserBillCategory.user_id == user_id).all()
            categories_ids = [cat.bill_category_id for cat in user_categories] if user_categories else []
            #Session.close()
            bill_categories = Session.query(BillCategory)\
                .join(TranslationBillCategory, BillCategory.id == TranslationBillCategory.bill_category_id)\
                .filter(BillCategory.id.notin_(categories_ids),
                        TranslationBillCategory.lang_code == lang_code)
        else:
            bill_categories = Session.query(BillCategory)\
                .join(UserBillCategory, BillCategory.id == UserBillCategory.bill_category_id)\
                .join(TranslationBillCategory, BillCategory.id == TranslationBillCategory.bill_category_id)\
                .filter(UserBillCategory.user_id == user_id,
                        TranslationBillCategory.lang_code == lang_code)
        if search:
            # bill_categories = bill_categories.filter(BillCategory.name.ilike('%{0}%'.format(search)))
            bill_categories = bill_categories.filter(
                TranslationBillCategory.translation_category_name.ilike('%{0}%'.format(search))
            )
        return bill_categories.all()

    @classmethod
    def user_settings_sub_categories(cls, active, user_id, search, lang_code='en'):
        # Get all active user categories
        user_categories = cls.user_settings_categories(active=True, user_id=user_id, search='', lang_code=lang_code)
        # Get all subcategories of active categories
        sub_cats = Session.query(BillSubCategory)\
            .filter(BillSubCategory.bill_category_id.in_([cat.id for cat in user_categories]))\
            .all() if user_categories else []
        #if not sub_cats:
            #db.session.close()
            #Session.close()
        if not active:
            # Get all active subcategories
            user_sub_categories = Session.query(UserBillSubCategory)\
                .filter(UserBillSubCategory.user_id == user_id,
                        UserBillSubCategory.bill_sub_category_id.in_([sub.id for sub in sub_cats]))\
                .all() if sub_cats else []
            # If not active subcategories for active categories return all subcategories for active categories
            if not user_sub_categories:
                #Session.close()
                return sub_cats
            # If active subcategories exist than return inactive subcategories of active categories
            sub_categories_ids = [sub_cat.bill_sub_category_id for sub_cat in
                                  user_sub_categories] if user_sub_categories else []
            sub_categories_ids_filter = [sub.id for sub in sub_cats if
                                         sub.id not in sub_categories_ids] if sub_categories_ids else []
            #Session.close()
            bill_sub_categories = Session.query(BillSubCategory)\
                .join(TranslationBillSubCategory,
                      BillSubCategory.id == TranslationBillSubCategory.bill_sub_category_id)\
                .filter(BillSubCategory.id.in_(sub_categories_ids_filter),
                        TranslationBillSubCategory.lang_code == lang_code)
            if not sub_categories_ids_filter:
                #db.session.close()
                #Session.close()
                return []
        else:
            bill_sub_categories = Session.query(BillSubCategory)\
                .join(UserBillSubCategory, BillSubCategory.id == UserBillSubCategory.bill_sub_category_id)\
                .join(TranslationBillSubCategory,
                      BillSubCategory.id == TranslationBillSubCategory.bill_sub_category_id)\
                .filter(UserBillSubCategory.user_id == user_id,
                        UserBillSubCategory.bill_sub_category_id.in_([sub.id for sub in sub_cats]),
                        TranslationBillSubCategory.lang_code == lang_code)
        if search:
            #bill_sub_categories = bill_sub_categories.filter(BillSubCategory.name.ilike('%{0}%'.format(search)))
            bill_sub_categories = bill_sub_categories.filter(
                TranslationBillSubCategory.translation_subcategory_name.ilike('%{0}%'.format(search))
            )
        return bill_sub_categories.all()

    @classmethod
    def save_or_delete_user_settings_category(cls, active, category_id, user_id):
        costs = len(BillProvider.get_costs_or_profits(
            category_id=category_id, sub_category_id=None, currency_id=None,
            user_id=user_id, bill_type='costs', bills_limit=None,
            bills_offset=None))
        profits = len(BillProvider.get_costs_or_profits(
            category_id=category_id, sub_category_id=None, currency_id=None,
            user_id=user_id, bill_type='profits', bills_limit=None,
            bills_offset=None))
        if not active:
            new_category = UserBillCategory()
            new_category.user_id = user_id
            new_category.bill_category_id = category_id
            # db.session.add(new_category)
            # db.session.commit()
            # db.session.close()
            Session.add(new_category)
            Session.commit()
            #Session.close()
            return True
        else:
            if costs or profits:
                return False
            user_category = Session.query(UserBillCategory)\
                .filter(UserBillCategory.user_id == user_id,
                        UserBillCategory.bill_category_id == category_id)\
                .first()
            user_sub_categories = Session.query(UserBillSubCategory)\
                .join(BillSubCategory, UserBillSubCategory.bill_sub_category_id == BillSubCategory.id) \
                .filter(BillSubCategory.bill_category_id == category_id,
                        UserBillSubCategory.user_id == user_id)\
                .all()
            if user_category:
                # db.session.delete(user_category)
                # db.session.commit()
                # db.session.close()
                Session.delete(user_category)
                Session.commit()
            if user_sub_categories:
                for sub_category in user_sub_categories:
                    # db.session.delete(sub_category)
                    # db.session.commit()
                    # db.session.close()
                    Session.delete(sub_category)
                    Session.commit
            #db.session.close()
            #Session.close()
            return True

    @classmethod
    def save_or_delete_user_settings_sub_category(cls, active, sub_category_id, user_id):
        costs = len(BillProvider.get_costs_or_profits(
            category_id=None, sub_category_id=sub_category_id, currency_id=None,
            user_id=user_id, bill_type='costs', bills_limit=None,
            bills_offset=None))
        profits = len(BillProvider.get_costs_or_profits(
            category_id=None, sub_category_id=sub_category_id, currency_id=None,
            user_id=user_id, bill_type='profits', bills_limit=None,
            bills_offset=None))
        if not active:
            new_sub_category = UserBillSubCategory()
            new_sub_category.user_id = user_id
            new_sub_category.bill_sub_category_id = sub_category_id
            # db.session.add(new_sub_category)
            # db.session.commit()
            # db.session.close()
            Session.add(new_sub_category)
            Session.commit()
            #Session.close()
            return True
        else:
            if costs or profits:
                return False
            user_sub_category = Session.query(UserBillSubCategory)\
                .filter(UserBillSubCategory.user_id == user_id,
                        UserBillSubCategory.bill_sub_category_id == sub_category_id)\
                .first()
            if user_sub_category:
                # db.session.delete(user_sub_category)
                # db.session.commit()
                # db.session.close()
                Session.delete(user_sub_category)
                Session.commit()
            #db.session.close()
            #Session.close()
            return True

    @classmethod
    def edit_user(cls, user_data, user_email, user_id):
        # First check new user email
        if cls.get_user_by_email(email=user_data['email']) and user_email != user_data['email']:
            #Session.close()
            return False, 'email'
        user = cls.get_user_by_ID(user_id=user_id)
        if user:
            try:
                user.gender = user_data['gender']
                user.email = user_data['email'] if regex(regex_string=user_data['email'],
                                                         email=True) else None
                user.city_id = u'{0}'.format(user_data['city_id'])
                user.address = u'{0}'.format(user_data['address'])
                if user_data['birthDate']:
                    user.birth_date = datetime.strptime(date_format(user_data['birthDate'], string=True, graph=False, birth_day=True), "%Y-%m-%d") #.strftime("%Y-%m-%d")
                user.first_name = u'{0}'.format(user_data['firstName']) if regex(regex_string=user_data['firstName'],
                                                                                 first_name=True) else None
                user.last_name = u'{0}'.format(user_data['lastName']) if regex(regex_string=user_data['lastName'],
                                                                               last_name=True) else None
                user.country_id = u'{0}'.format(user_data['country_id'])
                user.phone = u'{0}'.format(user_data['phone'])
                user.currency_id = u'{0}'.format(user_data['currency_id']) if user_data['currency_id'] != 'null' and user_data['currency_id'] != 'None' else None
                Session.commit()
            except Exception as ex:
                Session.rollback()
                print(ex)
                return False, 'regex'
        # if user.image_id < 5:
        #     user.image_id = 1 if user_data['gender'] == 'male' else user.image_id
        #     user.image_id = 2 if user_data['gender'] == 'female' else user.image_id

        # db.session.commit()
        # db.session.close()
        #Session.close()
        return True, None

    @classmethod
    def get_active_user_currencies_with_limit(cls, user_id):
        user_currencies = Session.query(UserCurrency)\
            .filter(UserCurrency.user_id == user_id)
        return user_currencies.all()

    @classmethod
    def edit_active_user_currencies_with_limit(cls, currency_id, monthly_limit):
        currency = Session.query(UserCurrency)\
            .filter(UserCurrency.id == currency_id)\
            .first()
        if currency:
            currency.monthly_cost_limit = monthly_limit
        # db.session.commit()
        # db.session.close()
        Session.commit()
        #Session.close()
        return True

    @classmethod
    def get_user_currency_by_currency_id(cls, currency_id):
        user_currency = Session.query(UserCurrency)\
            .join(Currency, UserCurrency.currency_id == Currency.id)\
            .filter(Currency.id == currency_id)
        return user_currency.first()

    @classmethod
    def get_all_user_news(cls, user_id):
        user_news = Session.query(News)\
            .join(UserNews, UserNews.news_id == News.id)\
            .filter(UserNews.hidden == False,
                    UserNews.user_id == user_id)\
            .order_by(News.created.desc())
        return user_news.all()

    @classmethod
    def hide_news_by_user_id_and_news_id(cls, user_id, news_id):
        news = Session.query(UserNews)\
            .filter(UserNews.news_id == news_id,
                    UserNews.user_id == user_id)\
            .first()
        if news:
            news.hidden = True
            Session.delete(news)
        # db.session.commit()
        # db.session.close()
        Session.commit()
        #Session.close()
        return True

    @classmethod
    def update_application_rating(cls, user, rating):
        user.application_rating = rating
        Session.commit()
        return True

