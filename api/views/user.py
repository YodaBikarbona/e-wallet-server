from flask import request
from flask import jsonify
import os
from api.model.config import db
from config import session as Session
from werkzeug.utils import secure_filename
from api.model.providers.user import UserProvider
from api.views.register_and_login import send_code_to_mail
from api.validation.user import EditUserSchema
from api.model.user import (
    User,
    Image
)
from api.serializer.serializers import (
    UsersSerializer,
    ImageSerializer,
    CurrencySerializer,
    CategorySerializer,
    SubCategorySerializer,
    UserCirrenciesSerializer,
    NewsSerializer,
    CategoryTranslationSerializer,
    SubCategoryTranslationSerializer
)
from api.helper.helper import (
    now,
    ValidateRequestSchema,
    error_handler,
    create_new_folder,
    ok_response,
    check_security_token,
    check_passwords,
    new_psw,
    date_format,
    password_regex,
)
from api.helper.translations import _translation
from api.model.config import (
    app,
    PROJECT_HOME,
    UPLOAD_FOLDER
)
from api.messages import (
    error_messages,
    messages
)


def user(request):
    """
    This function will get user information (Profile form)
    :param request:
        Authorization: string (User security token "headers")
    :return:
        user: dict (user information)
        user_id: int
        currencies: int (number of chosen user currencies)
        categories: int (number of chosen user categories)
        sub_categories: int (number of chosen user sub categories)
    """
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=error_messages.INVALID_TOKEN)
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=error_messages.USER_NOT_FOUND)
    additional_data = {
        'user': UsersSerializer(many=False).dump(usr).data,
        'user_id': usr.id,
    }
    user_currencies = UserProvider.check_user_currencies_number(user_id=usr.id)
    user_categories = UserProvider.check_user_categories_number(user_id=usr.id)
    user_sub_categories = UserProvider.check_user_sub_categories_number(user_id=usr.id)
    additional_data['user']['currencies'] = user_currencies if user_currencies else 0
    additional_data['user']['categories'] = user_categories
    additional_data['user']['sub_categories'] = user_sub_categories
    db.session.close()
    return ok_response("", additional_data)


def restart_password(request):
    """
    This function will send new restarted code to user email (Restart password form)
    :param request:
        email: string
    :return:
        message
    """
    usr = UserProvider.get_user_by_email(request.json['email'])
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=error_messages.EMAIL_USER_NOT_FOUND)
    UserProvider.set_new_restart_code(user=usr)
    send_code_to_mail(recipient=usr.email, code=usr.new_password_code)
    db.session.close()
    return ok_response(message=messages.RESTART_PASSWORD_CODE)


def restart_login_code(request):
    """
    This function will send new restarted code to user email if user doesn't get first time
    :param request:
        email: string
    :return:
        message
    """
    usr = UserProvider.get_user_by_email(request.json['email'])
    if not usr:
        Session.close()
        return error_handler(error_status=404, message=error_messages.EMAIL_USER_NOT_FOUND)
    UserProvider.set_new_login_code(user=usr)
    send_code_to_mail(recipient=usr.email, code=usr.code)
    Session.close()
    return ok_response(message=messages.RESTART_PASSWORD_CODE)


def user_settings_currencies(request):
    """
    This function will get all chosen user currencies,
    search is additional attribute (not required) which purpose
    is finding all currencies who include string inside name. Currencies
    could be active (that means user has already chosen that currency) and
    inactive (user has not already chosen that category)
    :param request:
        active: boolean
        search: string (not required)
        Authorization: string (User security token "headers")
    :return:
        message
        currencies: list (of currencies)
    """
    currency_active = request.json['active']
    search = request.json['search']
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    currencies = UserProvider.user_settings_currencies(
        active=currency_active,
        user_id=usr.id,
        search=search
    )
    additional_data = {
        "currencies": CurrencySerializer(many=True).dump(currencies).data if currencies else []
    }
    db.session.close()
    return ok_response(message=_translation(original_string=messages.SETTINGS_CURRENCIES, lang_code=lang),
                       additional_data=additional_data)


def user_settings_categories(request):
    """
    This function will get all chosen user categories,
    search is additional attribute (not required) which purpose
    is finding all categories who include string inside name. Categories
    could be active (that means user has already chosen that category) and
    inactive (user has not already chosen that category)
    :param request:
        active: boolean
        search: string (not required)
        Authorization: string (User security token "headers")
    :return:
        message
        categories: list (of categories)
    """
    category_active = request.json['active']
    search = request.json['search']
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    categories = UserProvider.user_settings_categories(
        active=category_active,
        user_id=usr.id,
        search=search,
        lang_code=lang
    )
    additional_data = {
        "categories": CategorySerializer(many=True).dump(categories).data if categories else []
    }
    for c in additional_data["categories"]:
        translation = [tr for tr in c["translations"] if tr.lang_code == lang]
        c["translations"] = CategoryTranslationSerializer(many=False).dump(translation[0]).data
    db.session.close()
    return ok_response(message=_translation(original_string=messages.SETTINGS_CATEGORIES, lang_code=lang),
                       additional_data=additional_data)


def user_settings_sub_categories(request):
    """
    This function will get all chosen user sub categories,
    function will get all sub categories connected with user
    categories, search is additional attribute (not required) which purpose
    is finding all sub categories who include string inside name. Sub categories
    could be active (that means user has already chosen that sub category) and
    inactive (user has not already chosen that sub category)
    :param request:
        active: boolean
        search: string (not required)
        Authorization: string (User security token "headers")
    :return:
        message
        sub_categories: list (of sub categories)
    """
    sub_category_active = request.json['active']
    search = request.json['search']
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    sub_categories = UserProvider.user_settings_sub_categories(
        active=sub_category_active,
        user_id=usr.id,
        search=search,
        lang_code=lang
    )
    additional_data = {
        "sub_categories": SubCategorySerializer(many=True).dump(sub_categories).data if sub_categories else []
    }
    for sc in additional_data["sub_categories"]:
        translation = [tr for tr in sc["translations"] if tr.lang_code == lang]
        sc["translations"] = SubCategoryTranslationSerializer(many=False).dump(translation[0]).data
        if sc["bill_category"]:
            c_translation = [trc for trc in sc['bill_category']['translations'] if trc.lang_code == lang]
            sc['bill_category']["translations"] = CategoryTranslationSerializer(many=False).dump(c_translation[0]).data
    db.session.close()
    return ok_response(message=_translation(original_string=messages.SETTINGS_SUB_CATEGORIES, lang_code=lang),
                       additional_data=additional_data)


def save_user_settings_currency(request):
    """
    This function will add new currency to user currencies,
    or delete currency from user currencies. Limit of user
    currencies is 10
    :param request:
        active: boolean
        currencyId: int
        Authorization: string (User security token "headers")
    :return:
        message: Empty message
    """
    currency_active = request.json['active']
    currency_id = request.json['currencyId']
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    if UserProvider.check_user_currencies_number(user_id=usr.id) == 10 and not currency_active:
        db.session.close()
        return error_handler(error_status=403, message=_translation(original_string=error_messages.MAX_CURRENCIES,
                                                                    lang_code=lang))
    if not UserProvider.save_or_delete_user_settings_currency(
        active=currency_active,
        currency_id=currency_id,
        user_id=usr.id
    ):
        db.session.close()
        return error_handler(error_status=403, message=_translation(original_string=error_messages.EXIST_CURRENCY_BILLS,
                                                                    lang_code=lang))
    db.session.close()
    return ok_response(message='')


def save_user_settings_category(request):
    """
    This function will add new category to user categories,
    or delete category from user categories
    :param request:
        active: boolean
        categoryId: int
        Authorization: string (User security token "headers")
    :return:
        message: Empty message
    """
    category_active = request.json['active']
    category_id = request.json['categoryId']
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    if not UserProvider.save_or_delete_user_settings_category(
        active=category_active,
        category_id=category_id,
        user_id=usr.id
    ):
        db.session.close()
        return error_handler(error_status=403, message=_translation(original_string=error_messages.EXIST_CATEGORY_BILLS,
                                                                    lang_code=lang))
    db.session.close()
    return ok_response(message='')


def save_user_settings_sub_category(request):
    """
    This function will add new sub category to user sub categories,
    or delete sub category from user sub categories
    :param request:
        active: boolean
        subCategoryId: int
        Authorization: string (User security token "headers")
    :return:
        message: empty message
    """
    sub_category_active = request.json['active']
    sub_category_id = request.json['subCategoryId']
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    if not UserProvider.save_or_delete_user_settings_sub_category(
        active=sub_category_active,
        sub_category_id=sub_category_id,
        user_id=usr.id
    ):
        db.session.close()
        return error_handler(error_status=403, message=_translation(
            original_string=error_messages.EXIST_SUBCATEGORY_BILLS,
            lang_code=lang))
    db.session.close()
    return ok_response(message='')


def restart_password_code(request):
    """
    This function will restart password code on button
    :param request:
        email: string
    :return:
        message: empty message
    """
    usr = UserProvider.get_user_by_email(request.json['email'])
    lang = request.headers['Lang']
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.EMAIL_USER_NOT_FOUND,
                                                                    lang_code=lang))
    if usr.new_password_code != request.json['code']:
        db.session.close()
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_CODE,
                                                                    lang_code=lang))
    if not UserProvider.check_expired_restart_code(user=usr, user_data=request.json):
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.INVALID_CODE,
                                                                    lang_code=lang))
    db.session.close()
    return ok_response(message='')


def save_new_password(request):
    """
    This function will save new user password (Restart password form)
    :param request:
        email: string
        password: string
        confirmPassword: string
    :return:
        message
    """
    usr = UserProvider.get_user_by_email(request.json['email'])
    lang = request.headers['Lang']
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.EMAIL_USER_NOT_FOUND,
                                                                    lang_code=lang))
    if request.json['newPassword'] != request.json['confirmPassword']:
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.PASSWORDS_NOT_SAME,
                                                                    lang_code=lang))
    if not password_regex(request.json['newPassword']):
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.PASSWORD_NOT_VALID,
                                                                    lang_code=lang))
    UserProvider.save_new_password(user=usr, user_data=request.json)
    db.session.close()
    return ok_response(message=_translation(original_string=messages.RESET_PASSWORD, lang_code=lang))


def upload_image(request): #, purpose='system_images/default_images/'):
    # claims = check_security_token(request.headers['Authorization'])
    # if claims:
    #     usr = UserProvider.get_user_by_ID(claims['user_id'])
    # else:
    #     return error_handler(403, error_messages.INVALID_TOKEN)
    # if not usr:
    #     return error_handler(404, error_messages.USER_NOT_FOUND)
    app.logger.info(PROJECT_HOME)
    if request.method == 'POST' and request.files['image']:
        app.logger.info(app.config['UPLOAD_FOLDER'])
        img = request.files['image']
        img_name = secure_filename(img.filename)
        folder = create_new_folder(app.config['UPLOAD_FOLDER']) #+ purpose if purpose else app.config['UPLOAD_FOLDER'])
        app.config['UPLOADED_PHOTOS_DEST'] = '/uploads'
        print(folder)
        saved_path = os.path.join(folder, img_name)
        print (saved_path)
        app.logger.info("saving {}".format(saved_path))
        #img.save(saved_path)
        # new_image = Image()
        # new_image.type = img_name.split('.')[1]
        # new_image.name = img_name.split('.')[0]
        # new_image.file_name = img_name
        # db.session.add(new_image)
        # db.session.commit()

        # usr = User.query.filter(User.id == usr.id).first()
        # usr.image_id = new_image.id
        # db.session.commit()
        #image = ImageSerializer(many=False).dump(new_image).data
        return jsonify(
            {
                'status': 'OK',
                'server_time': now().strftime("%Y-%m-%dT%H:%M:%S"),
                'code': 200,
                'msg': "Image is added!",
                #'image': image
            }
        )
        #return send_from_directory(app.config['UPLOAD_FOLDER'],img_name, as_attachment=True)
    else:
        return "Where is the image?"


def get_users(request, user_id):
    usr = UserProvider.get_user_by_ID(user_id=user_id)
    if not usr:
        db.session.close()
        return error_handler(400, error_messages.BAD_DATA)
    if not check_security_token(token=request.headers['Authorization'], user=usr):
        db.session.close()
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr.role.role_name == 'admin':
        db.session.close()
        return error_handler(403, error_messages.NOT_PERMISSION)
    users = UserProvider.get_all_users(user_id=user_id)
    additional_data = {
        "users": UsersSerializer(many=True).dump.data(users) if users else []
    }
    db.session.close()
    return ok_response(message=messages.USERS_LIST, additional_data=additional_data)


def change_password(request):
    """
    This method will change password via user interface (Change password button)
    :param request:
    :return: message
    """
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    if usr.password != new_psw(usr.salt, request.json['currentPassword']):
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.WRONG_PASSWORD,
                                                                    lang_code=lang))
    if 'newPassword' and 'confirmPassword' not in request.json:
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.BAD_DATA,
                                                                    lang_code=lang))
    if not check_passwords(request.json['newPassword'], request.json['confirmPassword']):
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.PASSWORDS_NOT_SAME,
                                                                    lang_code=lang))
    if not password_regex(request.json['newPassword']):
        db.session.close()
        return error_handler(400, error_messages.PASSWORD_NOT_VALID)
    UserProvider.save_new_password(user=usr, user_data=request.json)
    UserProvider.set_new_restart_code(user=usr, code=True)
    send_code_to_mail(recipient=usr.email, code=usr.code)
    db.session.close()
    return ok_response(message=_translation(original_string=messages.RESET_PASSWORD, lang_code=lang))


def edit_user(request):
    """
    This method will edit personal user information
    :param request:
    :return: message
    """
    lang = request.headers['Lang']
    if request.json['currency_id'] != 'null':
        request.json['currency_id'] = "{0}".format(request.json['currency_id'])
    if request.json['birthDate'] == 'null':
        request.json['birthDate'] = None
    if not ValidateRequestSchema(request, EditUserSchema()):
        return error_handler(error_status=400, message=_translation(original_string=error_messages.BAD_DATA,
                                                                    lang_code=lang))
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    status, response = UserProvider.edit_user(user_data=request.json, user_email=usr.email, user_id=usr.id)
    if not status:
        db.session.close()
        if response == 'email':
            return error_handler(error_status=400, message=_translation(
                original_string=error_messages.USER_ALREADY_EXISTS,
                lang_code=lang))
        else:
            return error_handler(error_status=400, message=_translation(original_string=error_messages.REGEX_ERROR,
                                                                        lang_code=lang))
    db.session.close()
    return ok_response(message=messages.USER_EDITED)


def get_active_currencies_limit(request):
    """
    This method will get all user active currencies with monthly limit
    :param request:
    :return: list_of_currencies
    """
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    active_currencies = UserProvider.get_active_user_currencies_with_limit(user_id=usr.id)
    additional_data = {
        'currencies': UserCirrenciesSerializer(many=True).dump(active_currencies).data if active_currencies else []
    }
    db.session.close()
    return ok_response(message=messages.ACTIVE_CURRENCIES, additional_data=additional_data)


def edit_currency_monthly_limit(request):
    """
    This method will edit monthly limit for specific currency (only active currencies)
    :param request:
    :return: message
    """
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    UserProvider.edit_active_user_currencies_with_limit(
        currency_id=request.json['currency_id'],
        monthly_limit=request.json['monthly_cost_limit']
    )
    active_currencies = UserProvider.get_active_user_currencies_with_limit(user_id=usr.id)
    additional_data = {
        'currencies': UserCirrenciesSerializer(many=True).dump(active_currencies).data if active_currencies else []
    }
    db.session.close()
    return ok_response(message=messages.MONTHLY_LIMIT_EDITED, additional_data=additional_data)


def get_news(request):
    """
    This method will get all news and information that user didn't hide
    :param request:
    :return:
    """
    claims = check_security_token(request.headers['Authorization'])
    lang = request.headers['Lang']
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    news = UserProvider.get_all_user_news(user_id=usr.id)
    news = NewsSerializer(many=True).dump(news).data if news else []
    for n in news:
        n['created'] = date_format(n['created'], string=True, graph=True)
    additional_data = {
        'news': news
    }
    Session.commit()
    return ok_response(message=messages.NEWS_LIST, additional_data=additional_data)


def clear_news(request):
    """
    This method will hide all news that user don't want to see anymore (Old news)
    :param request:
    :return:
    """
    lang = request.headers['Lang']
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    UserProvider.hide_news_by_user_id_and_news_id(user_id=usr.id, news_id=request.json['newsId'])
    db.session.close()
    return ok_response(message=messages.NEWS_HIDDEN)


def update_application_rating(request):
    lang = request.headers['Lang']
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(error_status=403, message=_translation(original_string=error_messages.INVALID_TOKEN,
                                                                    lang_code=lang))
    if not usr:
        db.session.close()
        return error_handler(error_status=404, message=_translation(original_string=error_messages.USER_NOT_FOUND,
                                                                    lang_code=lang))
    UserProvider.update_application_rating(user=usr, rating=request.json['rating'])
    db.session.close()
    return ok_response(message='')
