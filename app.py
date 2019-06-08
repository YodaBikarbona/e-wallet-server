from flask import Flask
from flask import request
from api.model.user import db
from flask_cors import CORS
from api.serializer.serializers import UsersSerializer, RoleSerializer, CountrySerializer, CitySerializer
from api.views.register_and_login import register, login, activate_user, logout
from api.views.user import user, upload_image, \
    get_users, restart_password, restart_password_code, \
    save_new_password, user_settings_currencies, save_user_settings_currency, \
    user_settings_sub_categories, user_settings_categories, save_user_settings_category, \
    save_user_settings_sub_category
from api.model.config import app
from api.helper.helper import ok_response
from flask import send_from_directory
from api.views.bill import (
    get_categories,
    get_sub_categories,
    get_currencies,
    add_bill,
    get_costs
)

#from api.model import user, country, bill
#db.create_all()


cors = CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/register', methods=['POST'])
def register_endpoint():

    return register(request)

@app.route('/login', methods=['POST'])
def login_endpoint():

    if "code" in request.json:
        activate_user(request)

    return login(request)

@app.route('/user', methods=['GET'])
def get_user_endpoint():

    return user(request)

@app.route('/upload/user', methods=['POST'])
def upload_endpoint():

    return upload_image(request)

@app.route('/dir/<path:path>', methods=['GET'])
def serve_file_in_dir_endpoint(path):

    var = '/home/oem/Desktop/Projects/E-wallet/e-wallet-server/api/model/uploads/'
    return send_from_directory(var, path)

@app.route('/logout', methods=['POST'])
def logout_endpoint():

    return logout(request)

@app.route('/restartPassword', methods=['POST'])
def restart_password_endpoint():

    return restart_password(request)

@app.route('/restartPasswordCode', methods=['POST'])
def restart_password_code_endpoint():

    return restart_password_code(request)

@app.route('/saveNewPassword', methods=['POST'])
def save_new_password_endpoint():

    return save_new_password(request)

@app.route('/test', methods=['GET'])
def test_endpoint():

    return "Hello"

@app.route('/countries', methods=['GET'])
def country_endpoint():
    from api.model.providers.other import OtherProvider

    countries = OtherProvider.get_countries()

    additional_data = {
        'countries': CountrySerializer(many=True).dump(countries).data
    }

    return ok_response("", additional_data)


@app.route('/countries/<int:country_id>/cities', methods=['GET'])
def city_endpoint(country_id):
    from api.model.providers.other import OtherProvider

    cities = OtherProvider.get_cities(country_id)

    additional_data = {
        'cities': CitySerializer(many=True).dump(cities).data
    }

    print(additional_data)

    return ok_response("", additional_data)


@app.route('/user/<int:id>/users', methods=['GET'])
def get_users_endpoint(id):

    return get_users(request=request, user_id=id)


@app.route('/bills/add_bill', methods=['POST'])
def add_new_bill_endpoint():

    return add_bill(request=request)


# @app.route('/bills/costs', methods=['GET'])
# def get_bills_endpoint(id):
#
#     return get_costs(request=request)

@app.route('/bills/costs', methods=['POST'])
def get_bills_endpoint():

    return get_costs(request=request)


@app.route('/user/<int:id>/categories', methods=['GET'])
def get_categories_endpoint(id):

    return get_categories(user_id=id)


@app.route('/user/<int:id>/category/<int:category_id>/sub_categories', methods=['GET'])
def get_sub_categories_endpoint(id, category_id):

    return get_sub_categories(user_id=id, category_id=category_id)


@app.route('/user/currencies', methods=['POST'])
def get_settings_currencies_endpoint():

    return user_settings_currencies(request)


@app.route('/user/categories', methods=['POST'])
def get_settings_categories_endpoint():

    return user_settings_categories(request)


@app.route('/user/sub_categories', methods=['POST'])
def get_settings_sub_categories_endpoint():

    return user_settings_sub_categories(request)


@app.route('/user/save_currency', methods=['POST'])
def save_user_settings_currency_endpoint():

    return save_user_settings_currency(request)


@app.route('/user/save_category', methods=['POST'])
def save_user_settings_category_endpoint():

    return save_user_settings_category(request)


@app.route('/user/save_sub_category', methods=['POST'])
def save_user_settings_sub_category_endpoint():

    return save_user_settings_sub_category(request)


@app.route('/user/<int:id>/currencies', methods=['GET'])
def get_currencies_endpoint(id):

    return get_currencies(user_id=id)


@app.route('/add_cat_subcat', methods=['GET'])
def add_subcat_endpoint():
    from api.model.bill import BillCategory, BillSubCategory
    from api.helper.constants import categories_and_subcategories
    for data in categories_and_subcategories:
        for k, v in data.items():
            category = BillCategory()
            category.name = k
            db.session.add(category)
            db.session.commit()
            for sub_c in v:
                sub_category = BillSubCategory()
                sub_category.name = sub_c
                sub_category.bill_category_id = category.id
                db.session.add(sub_category)
                db.session.commit()
    return 'True'

# @app.route('/add_categories', methods=['GET'])
# def add_cat_endpoint():
#
#
#     return 'True'





# @app.route('/country', methods=['GET'])
# def country_endpoint():
#     from api.model.country import Country
#     from api.helper.constants import countries
#     for c in countries:
#         country = Country()
#         country.name = c['name']
#         country.phone_code = c['phoneCode']
#         country.alpha2code = c['alpha2code']
#         country.alpha3code = c['alpha3code']
#         country.activated = True
#         db.session.add(country)
#         db.session.commit()
#
#     from api.model.country import Currency
#     from api.helper.constants import currencies
#     for c, k in currencies[0].items():
#         currency = Currency()
#         currency.name = k['name'].encode(encoding='UTF-8', errors='strict')
#         currency.symbol = ""  # k[u'symbol'].encode(encoding='UTF-8',errors='strict')
#         currency.symbol_native = ""  # k['symbol_native'].encode(encoding='UTF-8',errors='strict')
#         currency.code = k['code'].encode(encoding='UTF-8', errors='strict')
#         currency.name_plural = k['name_plural'].encode(encoding='UTF-8', errors='strict')
#         currency.activated = True
#         db.session.add(currency)
#         db.session.commit()
#
#     return "True"


# @app.route('/currency', methods=['GET'])
# def currency_endpoint():
#     from api.model.country import Currency
#     from api.helper.constants import currencies
#     for c, k in currencies[0].items():
#         currency = Currency()
#         currency.name = k['name'].encode(encoding='UTF-8',errors='strict')
#         currency.symbol = "" #k[u'symbol'].encode(encoding='UTF-8',errors='strict')
#         currency.symbol_native = "" #k['symbol_native'].encode(encoding='UTF-8',errors='strict')
#         currency.code = k['code'].encode(encoding='UTF-8',errors='strict')
#         currency.name_plural = k['name_plural'].encode(encoding='UTF-8',errors='strict')
#         currency.activated = True
#         db.session.add(currency)
#         db.session.commit()
#
#     return "True"




"""@app.route('/role', methods=['GET'])
def create_role():

    role = Role()
    role.role_name = 'user'
    role.deleted = False
    db.session.add(role)
    db.session.commit()
    return "True"""


if __name__ == '__main__':
    db.create_all()
    app.run()

