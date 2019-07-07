from flask import request
from api.model.user import User, Image
from flask import jsonify
from api.serializer.serializers import UsersSerializer, ImageSerializer
from api.helper.helper import now, ValidateRequestSchema, error_handler, create_new_folder, ok_response, check_security_token
import os
from api.model.config import app, PROJECT_HOME, UPLOAD_FOLDER
from werkzeug.utils import secure_filename
from api.model.config import db
from api.model.providers.user import UserProvider
from api.model.providers.bill import BillProvider
from api.messages import error_messages, messages
from api.validation.bill import NewBillSchema
from api.serializer.serializers import BillSerializer, CategorySerializer, SubCategorySerializer, CurrencySerializer


def add_bill(request):
    if not ValidateRequestSchema(request, NewBillSchema()):
        return error_handler(400, error_messages.BAD_DATA)
    user = UserProvider.get_user_by_ID(request.json['user_id'])
    if not check_security_token(token=request.headers['Authorization'], user=user):
        return error_handler(403, error_messages.INVALID_TOKEN)
    BillProvider.add_new_bill(bill_data=request.json)
    return ok_response(message=messages.BILL_ADDED)


def get_categories(user_id):
    # user = UserProvider.get_user_by_ID(user_id=user_id)
    # if not check_security_token(token=request.headers['Authorization'], user=user):
    #     return error_handler(403, error_messages.INVALID_TOKEN)
    categories = BillProvider.get_categories()
    additional_data = {
        'categories': CategorySerializer(many=True).dump(categories).data if categories else []
    }
    return ok_response(message='', additional_data=additional_data)


def get_sub_categories(user_id, category_id):
    # user = UserProvider.get_user_by_ID(user_id=user_id)
    # if not check_security_token(token=request.headers['Authorization'], user=user):
    #     return error_handler(403, error_messages.INVALID_TOKEN)
    sub_categories = BillProvider.get_sub_categories(category_id=category_id)
    additional_data = {
        'sub_categories': SubCategorySerializer(many=True).dump(sub_categories).data if sub_categories else []
    }
    return ok_response(message='', additional_data=additional_data)


def get_currencies(user_id):
    #user = UserProvider.get_user_by_ID(user_id=user_id)
    #if not check_security_token(token=request.headers['Authorization'], user=user):
    #    return error_handler(403, error_messages.INVALID_TOKEN)
    currencies = BillProvider.get_currencies() #[] #BillProvider.get_sub_categories(category_id=category_id)
    additional_data = {
        'currencies': CurrencySerializer(many=True).dump(currencies).data if currencies else []
    }
    return ok_response(message='', additional_data=additional_data)


def get_costs(request):
    """
    This function will save new user password (Restart password form)
    :param request:
        email: string
        password: string
        confirmPassword: string
    :return:
        message
    """
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr:
        return error_handler(404, error_messages.USER_NOT_FOUND)

    costs = BillProvider.get_costs(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        user_id=usr.id
    )
    additional_data = {
        'costs': BillSerializer(many=True).dump(costs).data if costs else []
    }
    return ok_response(message='', additional_data=additional_data)


def get_sub_categoryes_by_category(request):
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr:
        return error_handler(404, error_messages.USER_NOT_FOUND)
    sub_categories = BillProvider.get_sub_categories(category_id=request.json['category_id'])
    additional_data = {
        'sub_categories': SubCategorySerializer(many=True).dump(sub_categories).data if sub_categories else []
    }
    return ok_response(message='', additional_data=additional_data)
