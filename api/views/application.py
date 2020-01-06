from flask import request
from flask import jsonify
import os
from api.model.config import db
from config import session as Session
from werkzeug.utils import secure_filename
from api.model.providers.user import UserProvider
from api.model.providers.application import ApplicationProvider
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
    SubCategoryTranslationSerializer,
    BugsSerializer
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


def get_bugs(request):
    """
    This method will get all bugs was written by users
    :param request:
    :return: list_of_bugs
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
    bugs = ApplicationProvider.get_bugs()
    bugs = BugsSerializer(many=True).dump(bugs).data if bugs else []
    for n in bugs:
        n['created'] = date_format(n['created'], string=True)
    additional_data = {
        'bugs': bugs,
    }
    db.session.close()
    return ok_response(message='Bugs', additional_data=additional_data)


def add_new_bug(request):
    """
    This method will add new bug from users
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
    if not ApplicationProvider.add_new_bug(comment=request.json['comment'], user_id=usr.id):
        db.session.close()
        return error_handler(error_status=400, message='')
    db.session.close()
    return ok_response(message='')
