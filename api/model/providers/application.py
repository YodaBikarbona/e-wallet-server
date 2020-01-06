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
from api.model.application import (
    Bugs
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


class ApplicationProvider:

    @classmethod
    def get_bugs(cls):
        bugs = Session.query(Bugs).filter().order_by(Bugs.created.desc())
        return bugs.all()

    @classmethod
    def add_new_bug(cls, comment, user_id):
        try:
            bug = Bugs()
            bug.user_id = user_id
            bug.comment = comment
            bug.created = now()
            Session.add(bug)
            Session.commit()
            return True
        except Exception as ex:
            Session.rollback()
            print(ex)
