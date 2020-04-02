from flask import Flask, send_from_directory
import schedule
import time
from gevent.pywsgi import WSGIServer
from threading import Thread
from flask import request
from api.model.user import db
from flask_cors import CORS
from api.serializer.serializers import UsersSerializer, RoleSerializer, CountrySerializer, CitySerializer
from api.views.register_and_login import register, login, activate_user, logout
from api.views.user import (
    user,
    upload_image,
    get_users,
    restart_password,
    restart_password_code,
    restart_login_code,
    save_new_password,
    user_settings_currencies,
    save_user_settings_currency,
    user_settings_sub_categories,
    user_settings_categories,
    save_user_settings_category,
    save_user_settings_sub_category,
    change_password,
    edit_user,
    get_active_currencies_limit,
    edit_currency_monthly_limit,
    get_news,
    clear_news,
    update_application_rating
)
from api.views.application import (
    get_bugs,
    add_new_bug,
    add_new_suggestion
)
#from api.model.config import app
from config import app
from api.helper.helper import ok_response, date_format, now
from flask import send_from_directory
from api.views.bill import (
    get_categories,
    get_sub_categories,
    get_currencies,
    add_bill,
    get_costs,
    get_profits,
    get_sub_categoryes_by_category,
    new_costs,
    new_profits,
    print_pdf_report,
    get_graph,
    delete_bill,
    edit_bill,
)
from api.routes.get import get_route
from api.routes.post import post_route
from api.routes.put import put_route
from api.routes.delete import delete_route

#app = Flask(__name__, static_url_path='')

#from api.model import user, country, bill
db.create_all()


#----- Config------
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os

"""app = Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mihael:Mihael0110.@localhost/e_wallet?use_unicode=1&charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Flask

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

#app.config.from_pyfile('config.cfg')
mail = Mail(app)
app.config.from_pyfile('config.cfg')"""

#---------


cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/login', strict_slashes=False)
@app.route('/register', strict_slashes=False)
@app.route('/dashboard/profile', strict_slashes=False)
@app.route('/dashboard', strict_slashes=False)
@app.route('/restartPassword', strict_slashes=False)
@app.route('/dashboard/bills', strict_slashes=False)
@app.route('/dashboard/graph', strict_slashes=False)
@app.route('/dashboard/settings', strict_slashes=False)
@app.route('/dashboard/application', strict_slashes=False)
@app.route('/dashboard/application/bugs', strict_slashes=False)
@app.route('/dashboard/application/suggestions', strict_slashes=False)
@app.route('dashboard/application/info', strict_slashes=False)
@app.route('/', strict_slashes=False)
def root():
   return app.send_static_file('index.html')


@app.route(post_route.REGISTER, methods=['POST'])
def register_endpoint():
    return register(request)


@app.route(post_route.LOGIN, methods=['POST'])
def login_endpoint():
    if "code" in request.json:
        activate_user(request)
    return login(request)


@app.route(get_route.USER, methods=['GET'])
def get_user_endpoint():
    return user(request)


@app.route(post_route.UPLOAD_IMAGE, methods=['POST'])
def upload_endpoint():
    return upload_image(request)


@app.route(get_route.SERVE_FILE, methods=['GET'])
def serve_file_in_dir_endpoint(path):
    #This endpoint is removed from production (Heroku doesn't support upload images on their servers)
    #var = '/home/oem/Desktop/Projects/E-wallet/e-wallet-server/api/model/uploads/'
    print("--------------------------------------")
    var = '/app/api/model/uploads/'
    print(path)
    print(send_from_directory(var, path))
    return send_from_directory(var, path)


@app.route(post_route.LOGOUT, methods=['POST'])
def logout_endpoint():
    #This endpoint is no longer used (frontend function is on now)
    return logout(request)


@app.route(post_route.RESTART_PASSWORD, methods=['POST'])
def restart_password_endpoint():
    return restart_password(request)


@app.route(post_route.RESTART_LOGIN_CODE, methods=['POST'])
def restart_login_code_endpoint():
    return restart_login_code(request)


@app.route(post_route.RESTART_PASSWORD_CODE, methods=['POST'])
def restart_password_code_endpoint():
    return restart_password_code(request)


@app.route(post_route.SAVE_NEW_PASSWORD, methods=['POST'])
def save_new_password_endpoint():
    return save_new_password(request)


@app.route(post_route.GET_GRAPH, methods=['POST'])
def get_graph_endpoint():
    return get_graph(request)


@app.route(get_route.USER_NEWS, methods=['GET'])
def get_news_endpoint():
    return get_news(request)


@app.route(put_route.CLEAR_NEWS, methods=['PUT'])
def clear_news_endpoint():
    return clear_news(request)


@app.route(get_route.COUNTRIES, methods=['GET'])
def country_endpoint():
    from api.model.providers.other import OtherProvider
    countries = OtherProvider.get_countries()
    additional_data = {
        'countries': CountrySerializer(many=True).dump(countries).data
    }
    return ok_response("", additional_data)


@app.route(get_route.CITIES_BY_COUNTRY, methods=['GET'])
def city_endpoint(country_id):
    from api.model.providers.other import OtherProvider
    cities = OtherProvider.get_cities(country_id)
    additional_data = {
        'cities': CitySerializer(many=True).dump(cities).data
    }
    return ok_response("", additional_data)


@app.route('/v1/user/<int:id>/users', methods=['GET'])
def get_users_endpoint(id):
    return get_users(request=request, user_id=id)


@app.route(post_route.NEW_BILL, methods=['POST'])
def add_new_bill_endpoint():
    return add_bill(request=request)


# @app.route('/bills/costs', methods=['GET'])
# def get_bills_endpoint(id):
#     return get_costs(request=request)


@app.route('/v1/bills/costs', methods=['POST'])
def get_costs_endpoint():
    return get_costs(request=request)


@app.route('/v1/bills/profits', methods=['POST'])
def get_profits_endpoint():
    return get_profits(request=request)


@app.route(post_route.NEW_COSTS, methods=['POST'])
def new_costs_endpoint():
    return new_costs(request=request)


@app.route(post_route.NEW_PROFITS, methods=['POST'])
def new_profits_endpoint():
    return new_profits(request=request)


@app.route('/v1/user/category/sub_categories', methods=['POST'])
def get_sub_categoryes_by_category_endpoint():
    return get_sub_categoryes_by_category(request=request)


@app.route('/v1/user/<int:id>/categories', methods=['GET'])
def get_categories_endpoint(id):
    return get_categories(user_id=id)


@app.route('/v1/user/<int:id>/category/<int:category_id>/sub_categories', methods=['GET'])
def get_sub_categories_endpoint(id, category_id):
    return get_sub_categories(user_id=id, category_id=category_id)


@app.route(post_route.USER_CURRENCIES, methods=['POST'])
def get_settings_currencies_endpoint():
    return user_settings_currencies(request)


@app.route(post_route.USER_CATEGORIES, methods=['POST'])
def get_settings_categories_endpoint():
    return user_settings_categories(request)


@app.route(post_route.USER_SUB_CATEGORIES, methods=['POST'])
def get_settings_sub_categories_endpoint():
    return user_settings_sub_categories(request)


@app.route(post_route.SAVE_USER_CURRENCY, methods=['POST'])
def save_user_settings_currency_endpoint():
    """
    This method will add or delete user currencies
    :return: user_currencies
    """
    return save_user_settings_currency(request)


@app.route(post_route.SAVE_USER_CATEGORY, methods=['POST'])
def save_user_settings_category_endpoint():
    """
    This method will add or delete user categories
    :return: user_categories
    """
    return save_user_settings_category(request)


@app.route(post_route.SAVE_USER_SUB_CATEGORY, methods=['POST'])
def save_user_settings_sub_category_endpoint():
    """
    This method will add or delete user sub categories
    :return: user_sub_categories
    """
    return save_user_settings_sub_category(request)


@app.route(post_route.CHANGE_PASSWORD, methods=['POST'])
def change_password_endpoint():
    return change_password(request)


@app.route('/v1/user/<int:id>/currencies', methods=['GET'])
def get_currencies_endpoint(id):

    return get_currencies(user_id=id)


@app.route(post_route.PRINT_REPORT, methods=['POST'])
def print_report():
    return print_pdf_report(request)


@app.route(put_route.EDIT_USER, methods=['PUT'])
def edit_user_endpoint():
    return edit_user(request)


@app.route(post_route.GET_ACTIVE_CURRENCIES_LIMIT, methods=['POST'])
def get_active_currencies_limit_endpoint():
    return get_active_currencies_limit(request)


@app.route(put_route.EDIT_MONTHLY_LIMIT, methods=['PUT'])
def edit_currency_monthly_limit_endpoint():
    return edit_currency_monthly_limit(request)


@app.route(delete_route.DELETE_BILL, methods=['DELETE'])
def delete_bill_endpoint(id):
    return delete_bill(request, id)


@app.route(post_route.EDIT_BILL, methods=['POST'])
def edit_bill_endpoint(id):
    return edit_bill(request, id)


@app.route(post_route.APPLICATION_RATING, methods=['POST'])
def update_application_rating_endpoint():
    return update_application_rating(request)


@app.route(get_route.BUGS, methods=['GET'])
def get_bugs_endpoint():
    return get_bugs(request)


@app.route(post_route.ADD_BUG, methods=['POST'])
def add_new_bug_endpoint():
    return add_new_bug(request)


@app.route(post_route.ADD_SUGGESTION, methods=['POST'])
def add_new_suggestion_endpoint():
    return add_new_suggestion(request)

# # Push notification
# @app.route("/subscription/", methods=["GET", "POST"])
# def subscription():
#     """
#         POST creates a subscription
#         GET returns vapid public key which clients uses to send around push notification
#     """
#     from flask import Response
#     import json
#     from api.helper.helper import VAPID_PUBLIC_KEY
#     if request.method == "GET":
#         return Response(response=json.dumps({"public_key": VAPID_PUBLIC_KEY}),
#             headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")
#
#     subscription_token = request.get_json("subscription_token")
#     return Response(status=201, mimetype="application/json")

@app.route('/v1/add_cat_subcat', methods=['GET'])
def add_subcat_endpoint():
    # One of admin endpoints (later will be admin panel implemented and this will be moved)
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

@app.route('/update_user_role', methods=['GET'])
def update_user_role():
    # One of admin endpoints (later will be admin panel implemented and this will be moved)
    from api.model.user import User
    user = User.query.filter(User.id == 1).first()
    user.role_id = 1
    db.session.commit()

    return 'True'


# @app.route('/country', methods=['GET'])
# def country_endpoint_add():
#     One of admin endpoints (later will be admin panel implemented and this will be moved)
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
#         currency.name = k['name']#.encode(encoding='UTF-8', errors='strict')
#         currency.symbol = ""  # k[u'symbol'].encode(encoding='UTF-8',errors='strict')
#         currency.symbol_native = ""  # k['symbol_native'].encode(encoding='UTF-8',errors='strict')
#         currency.code = k['code']#.encode(encoding='UTF-8', errors='strict')
#         currency.name_plural = k['name_plural']#.encode(encoding='UTF-8', errors='strict')
#         currency.activated = True
#         db.session.add(currency)
#         db.session.commit()
#     return "True"


# Add new city
# @app.route('/v1/city/add', methods=['POST'])
# def add_new_city():
#     One of admin endpoints (later will be admin panel implemented and this will be moved)
#     from api.model.user import City
#     e_city = City.query.filter(City.name == request.json['name'],
#                                City.country_id == request.json['country_id']).first()
#     if not e_city:
#         city = City()
#         city.created = now()
#         city.country_id = request.json['country_id']
#         city.name = request.json['name']
#         db.session.add(city)
#         db.session.commit()
#     return "True"

# @app.route('/user_route', methods=['GET'])
# def user_route():
#     from api.model.user import User
#     user = User.query.filter().first()
#     if user:
#         user.activated = True
#         user.code = None
#         db.session.commit()
#     return 'True'

# @app.route('/currency', methods=['GET'])
# def currency_endpoint():
#     One of admin endpoints (later will be admin panel implemented and this will be moved)
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
#     return "True"


def job():
    if date_format(now()).split('.')[0] == '1':
        print('New month started!')
    print("I'm working...")
#
# #schedule.every(10).minutes.do(job)
# #schedule.every().hour.do(job)
# #schedule.every().day.at("10:30").do(job)
# #schedule.every(5).to(10).minutes.do(job)
# #schedule.every().monday.do(job)
# #schedule.every().wednesday.at("13:15").do(job)
# #schedule.every().minute.at(":17").do(job)
# schedule.every(5).seconds.do(job)
#
#
# #schedule.every().day.at("00:04:00").do(job)
#
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# def main():
#     db.create_all()
#     # app.run()
#     app.run(host="192.168.0.25", debug=True, port=5000, use_reloader=False)

# def prin():
#     print('This is function in thread')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, use_reloader=False)

# schedule.every().day.at("00:00:00").do(job)
# t = Thread(target=run_schedule)
# t.start()
# #app_server = WSGIServer(("192.168.0.25", 5000), app)
# #app_server.serve_forever()
# app_server.serve_forever()

"""
Schedule not working, investigate why.
"""






