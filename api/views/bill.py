from flask import request
from api.model.user import User, Image
from flask import jsonify
from api.serializer.serializers import UsersSerializer, ImageSerializer
from api.helper.helper import now, ValidateRequestSchema, error_handler, create_new_folder, ok_response, check_security_token, date_format, all_days_between_two_date
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
    This function will get all bills type costs
    :param request:
    :return: costs
    """
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr:
        return error_handler(404, error_messages.USER_NOT_FOUND)

    costs = BillProvider.get_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        user_id=usr.id,
        bill_type='costs',
        bills_limit=request.json['billsLimit'],
        bills_offset=request.json['billsOffset'],
    )
    additional_data = {
        'costs': BillSerializer(many=True).dump(costs).data if costs else [],
        'costs_length_list': BillProvider.count_costs_or_profits(
            category_id=request.json['categoryId'],
            sub_category_id=request.json['subCategoryId'],
            currency_id=request.json['currencyId'],
            user_id=usr.id,
            bill_type='costs'
        )
    }
    return ok_response(message='', additional_data=additional_data)


def new_costs(request):
    """
    This function will create new bills type costs
    :param request:
    :return:
    """
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr:
        return error_handler(404, error_messages.USER_NOT_FOUND)

    BillProvider.new_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        title=request.json['title'],
        comment = request.json['comment'] if 'comment' in request.json else "",
        price = request.json['price'],
        user_id=usr.id,
        bill_type='costs')
    return ok_response(message='')


def new_profits(request):
    """
    This function will create new bills type profits
    :param request:
    :return:
    """
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr:
        return error_handler(404, error_messages.USER_NOT_FOUND)

    BillProvider.new_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        title=request.json['title'],
        comment = request.json['comment'] if 'comment' in request.json else "",
        price = request.json['price'],
        user_id=usr.id,
        bill_type='profits')
    return ok_response(message='')


def get_profits(request):
    """
    This function will get all bills type profits
    :param request:
    :return: profits
    """
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr:
        return error_handler(404, error_messages.USER_NOT_FOUND)

    profits = BillProvider.get_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        user_id=usr.id,
        bill_type='profits',
        bills_limit=request.json['billsLimit'],
        bills_offset=request.json['billsOffset'],
    )
    additional_data = {
        'profits': BillSerializer(many=True).dump(profits).data if profits else [],
        'profits_length_list': BillProvider.count_costs_or_profits(
            category_id=request.json['categoryId'],
            sub_category_id=request.json['subCategoryId'],
            currency_id=request.json['currencyId'],
            user_id=usr.id,
            bill_type='profits'
        )
    }
    return ok_response(message='', additional_data=additional_data)


def get_sub_categoryes_by_category(request):
    """
    This function will get all sub categories by picked category
    :param request:
    :return: sub_categories
    """
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


def print_pdf_report(request):
    """
    This function will create report as html template and convert report to pdf.
    Consuming this function user will download report of bills
    :return: PDF
    """
    from flask import render_template, make_response
    import pdfkit
    from manage import _get_pdfkit_config
    #import pydf

    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr:
        return error_handler(404, error_messages.USER_NOT_FOUND)
    user = UsersSerializer(many=False).dump(usr).data
    bills = BillProvider.get_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        user_id=usr.id,
        bill_type=request.json['billType']
    )
    bills = BillSerializer(many=True).dump(bills).data if bills else []
    #items = len(BillProvider.get_costs_or_profits('null', 'null', 'null', user_id=usr.id, bill_type=request.json['billType'], bills=bills))
    summ = 0
    list_of_currencies = []
    for i, bill in enumerate(bills):
        bill['sequence'] = i+1
        if bill['bill_sub_category_id'] != False:
            bill_sub_category = BillProvider.get_subcategory_by_sub_cat_id(bill_sub_category_id=bill['bill_sub_category_id'])
            bill['bill_sub_category'] = SubCategorySerializer(many=False).dump(bill_sub_category).data
        bill['created'] = date_format(bill['created'], string=True)
        summ += bill['price']
        if bill['currency']['code'] not in list_of_currencies:
            list_of_currencies.append(bill['currency']['code'])
    currencies = ", ".join(list_of_currencies)
    summ_list = []
    for c in list_of_currencies:
        summ = 0
        for bill in bills:
            if c == bill['currency']['code']:
                summ += bill['price']
        summ_list.append({'currency': c,
                          'summ': round(summ, 2)})
    items = len(bills)
    scss = ['static/report/report.scss']
    rendered = render_template("report_template.html", user=user, items=items, report_date=date_format(now()),
                               bills=bills, bill_type=request.json['billType'], currencies=currencies, summ=summ_list)
    report = pdfkit.from_string(rendered, True, css=scss, configuration=_get_pdfkit_config())
    #report = pydf.generate_pdf(html=rendered)
    response = make_response(report)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response


def get_graph(request):
    """
    This method will get all bills with date and prices (added for each day)
    :param request:
    :return: list_of_prices (cost and profit)
    """
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr:
        return error_handler(404, error_messages.USER_NOT_FOUND)
    bills = BillProvider.get_all_costs_and_profits(
        costs=request.json['costs'],
        profits=request.json['profits'],
        user_id=usr.id,
        currency_id=request.json['currency_id']
    )
    bills = BillSerializer(many=True).dump(bills).data if bills else []
    bills = sorted(bills, key=lambda i: i['created'])
    bills_dates = []
    for i, bill in enumerate(bills):
        bill['sequence'] = i+1
        bill['created'] = date_format(bill['created'], string=True, graph=True)
        if bill['created'] not in bills_dates:
            bills_dates.append(bill['created'])
    all_days = []
    if bills_dates:
        all_days = all_days_between_two_date(start_date=bills_dates[0], end_date=bills_dates[-1])
    costs_list = [b for b in bills if b['bill_type'] == 'costs']
    profits_list = [b for b in bills if b['bill_type'] == 'profits']
    bills_list = []
    for date in all_days:
        sum_cost = 0
        sum_profit = 0
        for cost in costs_list:
            if date == cost['created']:
                sum_cost += cost['price']
        bills_list.append([date, 'Cost', sum_cost])
        for profit in profits_list:
            if date == profit['created']:
                sum_profit += profit['price']
        bills_list.append([date, 'Profit', sum_profit])
    bills_prices_cost = list(set([bill[-1] for bill in bills_list if bill[-2] == 'Cost' and bill[-1] != 0]))
    min_cost = min(bills_prices_cost) if bills_prices_cost else 0
    max_cost = max(bills_prices_cost) if bills_prices_cost else 0
    bills_prices_profit = list(set([bill[-1] for bill in bills_list if bill[-2] == 'Profit' and bill[-1] != 0]))
    min_profit = min(bills_prices_profit) if bills_prices_profit else 0
    max_profit = max(bills_prices_profit) if bills_prices_profit else 0
    currency = UserProvider.get_user_currency_by_currency_id(currency_id=request.json['currency_id'])
    additional_data = {
        'bills': bills_list,
        'min_cost': min_cost,
        'max_cost': max_cost,
        'min_profit': min_profit,
        'max_profit': max_profit,
        'monthly_limit': currency.monthly_cost_limit
    }
    return ok_response(message='Bills', additional_data=additional_data)


def delete_bill(request, bill_id):
    """
    This function will delete chosen bill
    :param request:
    :return:
    """
    claims = check_security_token(request.headers['Authorization'])
    if claims:
        usr = UserProvider.get_user_by_ID(claims['user_id'])
    else:
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not usr:
        return error_handler(404, error_messages.USER_NOT_FOUND)
    BillProvider.delete_bill_by_bill_id(bill_id=bill_id)
    return ok_response(message=messages.BILL_DELETED)
