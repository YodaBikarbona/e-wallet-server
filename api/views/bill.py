from flask import request, render_template, make_response
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
import pdfkit
from manage import _get_pdfkit_config
from api.helper.translations import _translation


def add_bill(request):
    if not ValidateRequestSchema(request, NewBillSchema()):
        return error_handler(400, error_messages.BAD_DATA)
    user = UserProvider.get_user_by_ID(request.json['user_id'])
    if not check_security_token(token=request.headers['Authorization'], user=user):
        db.session.close()
        return error_handler(403, error_messages.INVALID_TOKEN)
    if not BillProvider.add_new_bill(bill_data=request.json):
        db.session.close()
        return error_handler(error_status=400, message=error_messages.REGEX_ERROR)
    db.session.close()
    return ok_response(message=messages.BILL_ADDED)


def get_categories(user_id):
    # user = UserProvider.get_user_by_ID(user_id=user_id)
    # if not check_security_token(token=request.headers['Authorization'], user=user):
    #     return error_handler(403, error_messages.INVALID_TOKEN)
    categories = BillProvider.get_categories()
    additional_data = {
        'categories': CategorySerializer(many=True).dump(categories).data if categories else []
    }
    db.session.close()
    return ok_response(message='', additional_data=additional_data)


def get_sub_categories(user_id, category_id):
    # user = UserProvider.get_user_by_ID(user_id=user_id)
    # if not check_security_token(token=request.headers['Authorization'], user=user):
    #     return error_handler(403, error_messages.INVALID_TOKEN)
    sub_categories = BillProvider.get_sub_categories(category_id=category_id)
    additional_data = {
        'sub_categories': SubCategorySerializer(many=True).dump(sub_categories).data if sub_categories else []
    }
    db.session.close()
    return ok_response(message='', additional_data=additional_data)


def get_currencies(user_id):
    #user = UserProvider.get_user_by_ID(user_id=user_id)
    #if not check_security_token(token=request.headers['Authorization'], user=user):
    #    return error_handler(403, error_messages.INVALID_TOKEN)
    currencies = BillProvider.get_currencies() #[] #BillProvider.get_sub_categories(category_id=category_id)
    additional_data = {
        'currencies': CurrencySerializer(many=True).dump(currencies).data if currencies else []
    }
    db.session.close()
    return ok_response(message='', additional_data=additional_data)


def get_costs(request):
    """
    This function will get all bills type costs
    :param request:
    :return: costs
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

    costs = BillProvider.get_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        user_id=usr.id,
        bill_type='costs',
        bills_limit=request.json['billsLimit'],
        bills_offset=request.json['billsOffset'],
        search=request.json['search'],
        date_from=request.json['dateFrom'],
        date_to=request.json['dateTo']
    )
    additional_data = {
        'costs': BillSerializer(many=True).dump(costs).data if costs else [],
        'costs_length_list': BillProvider.count_costs_or_profits(
            category_id=request.json['categoryId'],
            sub_category_id=request.json['subCategoryId'],
            currency_id=request.json['currencyId'],
            user_id=usr.id,
            bill_type='costs',
            search=request.json['search'],
            date_from=request.json['dateFrom'],
            date_to=request.json['dateTo']
        )
    }
    db.session.close()
    return ok_response(message='', additional_data=additional_data)


def new_costs(request):
    """
    This function will create new bills type costs
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
    print(request.json)
    try:
        request.json['quantity'] = float(request.json['quantity'])
        if request.json['quantity'] <= 0:
            request.json['quantity'] = 1.00
    except Exception as ex:
        print(ex)
        request.json['quantity'] = 1.00
    if not BillProvider.new_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        title=request.json['title'],
        comment=request.json['comment'] if 'comment' in request.json else "",
        price=request.json['price'],
        user_id=usr.id,
        bill_type='costs',
        quantity=request.json['quantity'],
        not_my_city=request.json['notMyCity'],
        created=request.json['created']
    ):
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.REGEX_ERROR,
                                                                    lang_code=lang))
    db.session.close()
    return ok_response(message='')


def new_profits(request):
    """
    This function will create new bills type profits
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
    try:
        request.json['quantity'] = float(request.json['quantity'])
        if request.json['quantity'] <= 0:
            request.json['quantity'] = 1.00
    except Exception as ex:
        print(ex)
        request.json['quantity'] = 1.00
    if not BillProvider.new_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        title=request.json['title'],
        comment=request.json['comment'] if 'comment' in request.json else "",
        price=request.json['price'],
        user_id=usr.id,
        bill_type='profits',
        quantity=request.json['quantity'],
        not_my_city=request.json['notMyCity'],
        created=request.json['created']
    ):
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.REGEX_ERROR,
                                                                    lang_code=lang))
    db.session.close()
    return ok_response(message='')


def get_profits(request):
    """
    This function will get all bills type profits
    :param request:
    :return: profits
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

    profits = BillProvider.get_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        user_id=usr.id,
        bill_type='profits',
        bills_limit=request.json['billsLimit'],
        bills_offset=request.json['billsOffset'],
        search=request.json['search'],
        date_from=request.json['dateFrom'],
        date_to=request.json['dateTo']
    )
    additional_data = {
        'profits': BillSerializer(many=True).dump(profits).data if profits else [],
        'profits_length_list': BillProvider.count_costs_or_profits(
            category_id=request.json['categoryId'],
            sub_category_id=request.json['subCategoryId'],
            currency_id=request.json['currencyId'],
            user_id=usr.id,
            bill_type='profits',
            search=request.json['search'],
            date_from=request.json['dateFrom'],
            date_to=request.json['dateTo']
        )
    }
    db.session.close()
    return ok_response(message='', additional_data=additional_data)


def get_sub_categoryes_by_category(request):
    """
    This function will get all sub categories by picked category
    :param request:
    :return: sub_categories
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
    sub_categories = BillProvider.get_sub_categories(category_id=request.json['category_id'], user_id=usr.id)
    additional_data = {
        'sub_categories': SubCategorySerializer(many=True).dump(sub_categories).data if sub_categories else []
    }
    db.session.close()
    return ok_response(message='', additional_data=additional_data)


def print_pdf_report(request):
    """
    This function will create report as html template and convert report to pdf.
    Consuming this function user will download report of bills
    :return: PDF
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
    user = UsersSerializer(many=False).dump(usr).data
    bills = BillProvider.get_costs_or_profits(
        category_id=request.json['categoryId'],
        sub_category_id=request.json['subCategoryId'],
        currency_id=request.json['currencyId'],
        user_id=usr.id,
        bill_type=request.json['billType'],
        search=request.json['search'],
        date_from=request.json['dateFrom'],
        date_to=request.json['dateTo']
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
    # Production report
    report = pdfkit.from_string(rendered, False, css=scss, configuration=_get_pdfkit_config())
    # Localhost report
    # report = pdfkit.from_string(rendered, False, css=scss)
    response = make_response(report)
    db.session.close()
    if bills:
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
        return response
    else:
        return error_handler(error_status=404, message=_translation(original_string=error_messages.PRINT_PDF_ERROR,
                                                                    lang_code=lang))


def get_graph(request):
    """
    This method will get all bills with date and prices (added for each day)
    :param request:
    :return: list_of_prices (cost and profit)
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
    bills = BillProvider.get_all_costs_and_profits(
        costs=request.json['costs'],
        profits=request.json['profits'],
        user_id=usr.id,
        currency_id=request.json['currency_id'],
        date_from=request.json['dateFrom'],
        date_to=request.json['dateTo']
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
    bill_categories = []
    bill_sub_categories = []
    category_list = list(set([b['bill_category']['name'] for b in bills]))
    sub_category_list = list(set([b['bill_sub_category']['name'] for b in bills if b['bill_sub_category']]))
    bills_list = []
    # Four pie graphs
    bill_categories_list_cost = []
    bill_categories_list_profit = []
    bill_sub_categories_list_cost = []
    bill_sub_categories_list_profit = []
    for date in all_days:
        sum_cost = 0
        sum_profit = 0
        for cost in costs_list:
            if date == cost['created']:
                sum_cost += cost['price']
        bills_list.append([date, _translation(original_string='Cost', lang_code=lang), sum_cost])
        for profit in profits_list:
            if date == profit['created']:
                sum_profit += profit['price']
        bills_list.append([date, _translation(original_string='Profit', lang_code=lang), sum_profit])
    # Pie category graph
    for cat in category_list:
        sum_cost = 0
        sum_profit = 0
        for cost in costs_list:
            if cat == cost['bill_category']['name']:
                sum_cost += cost['price']
        if sum_cost > 0:
            bill_categories_list_cost.append({"label": "{0}".format(cat), "value": sum_cost})
        for profit in profits_list:
            if cat == profit['bill_category']['name']:
                sum_profit += profit['price']
        if sum_profit > 0:
            bill_categories_list_profit.append({"label": "{0}".format(cat), "value": sum_profit})
    # Pie sub category graph
    for sub_cat in sub_category_list:
        sum_cost = 0
        sum_profit = 0
        for cost in costs_list:
            if cost['bill_sub_category'] and sub_cat == cost['bill_sub_category']['name']:
                sum_cost += cost['price']
        if sum_cost > 0:
            bill_sub_categories_list_cost.append({"label": "{0}".format(sub_cat), "value": sum_cost})
        for profit in profits_list:
            if profit['bill_sub_category'] and sub_cat == profit['bill_sub_category']['name']:
                sum_profit += profit['price']
        if sum_profit > 0:
            bill_sub_categories_list_profit.append({"label": "{0}".format(sub_cat), "value": sum_profit})
    bills_prices_cost = list(set([bill[-1] for bill in bills_list if bill[-2] == _translation(
        original_string='Cost', lang_code=lang) and bill[-1] != 0]))
    min_cost = min(bills_prices_cost) if bills_prices_cost else 0
    max_cost = max(bills_prices_cost) if bills_prices_cost else 0
    bills_prices_profit = list(set([bill[-1] for bill in bills_list if bill[-2] == _translation(
        original_string='Profit', lang_code=lang) and bill[-1] != 0]))
    min_profit = min(bills_prices_profit) if bills_prices_profit else 0
    max_profit = max(bills_prices_profit) if bills_prices_profit else 0
    currency = UserProvider.get_user_currency_by_currency_id(currency_id=request.json['currency_id'])
    additional_data = {
        'bills': bills_list,
        'min_cost': min_cost,
        'max_cost': max_cost,
        'min_profit': min_profit,
        'max_profit': max_profit,
        'monthly_limit': currency.monthly_cost_limit,
        'bill_categories_list_cost': bill_categories_list_cost,
        'bill_categories_list_profit': bill_categories_list_profit,
        'bill_sub_categories_list_cost': bill_sub_categories_list_cost,
        'bill_sub_categories_list_profit': bill_sub_categories_list_profit,
        'costs': round(sum([b['price'] for b in bills if b['bill_type'] == 'costs']), 2),
        'profits': round(sum([b['price'] for b in bills if b['bill_type'] == 'profits']), 2),
    }
    db.session.close()
    return ok_response(message='Bills', additional_data=additional_data)


def delete_bill(request, bill_id):
    """
    This function will delete chosen bill
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
    if not BillProvider.delete_bill_by_bill_id(bill_id=bill_id):
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.BAD_DATA,
                                                                    lang_code=lang))
    db.session.close()
    return ok_response(message=_translation(original_string=messages.BILL_DELETED, lang_code=lang))


def edit_bill(request, bill_id):
    """
    This function will edit chosen bill
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
    if not BillProvider.edit_bill_by_bill_id(bill_id=bill_id, data=request.json):
        db.session.close()
        return error_handler(error_status=400, message=_translation(original_string=error_messages.BAD_DATA,
                                                                    lang_code=lang))
    db.session.close()
    return ok_response(message=_translation(original_string=messages.BILL_DELETED, lang_code=lang))
