from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, Unicode, Column, Date, Float
from sqlalchemy.orm import relationship
from api.helper.helper import now, new_salt, new_psw
from api.model.config import db
from api.model.user import User, Image
from api.model.country import Currency


class Bill(db.Model):
    __tablename__ = 'bill'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    title = Column(Unicode(255), nullable=False)
    comment = Column(Unicode(255), nullable=True)
    price = Column(Float, nullable=False)
    bill_type = Column(Unicode(255), nullable=False)
    not_my_city = Column(Boolean, default=False)
    quantity = Column(Float, default=1)

    currency_id = Column(Integer, ForeignKey('currency.id', ondelete='CASCADE'), nullable=True)
    image_id = Column(Integer, ForeignKey('image.id', ondelete='CASCADE'), nullable=True)
    bill_category_id = Column(Integer, ForeignKey('bill_category.id', ondelete='CASCADE'), nullable=True)
    bill_sub_category_id = Column(Integer, ForeignKey('bill_sub_category.id', ondelete='CASCADE'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    bill_category = relationship('BillCategory')
    bill_sub_category = relationship('BillSubCategory')
    image = relationship('Image')
    user = relationship('User')
    currency = relationship('Currency')

    def __repr__(self):
        return self.title


class BillCategory(db.Model):
    __tablename__ = 'bill_category'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    name = Column(Unicode(255), nullable=False)
    cost_type = Column(Boolean, nullable=True)
    profit_type = Column(Boolean, nullable=True)

    def __repr__(self):
        return self.name


class BillSubCategory(db.Model):
    __tablename__ = 'bill_sub_category'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    name = Column(Unicode(255), nullable=False)

    bill_category_id = Column(Integer, ForeignKey('bill_category.id', ondelete='CASCADE'), nullable=False)

    bill_category = relationship('BillCategory')

    def __repr__(self):
        return self.name


class UserBillCategory(db.Model):
    __tablename__ = 'user_bill_category'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    bill_category_id = Column(Integer, ForeignKey('bill_category.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User')
    bill_category = relationship('BillCategory')

    def __repr__(self):
        return self.bill_category.name


class UserBillSubCategory(db.Model):
    __tablename__ = 'user_bill_sub_category'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    bill_sub_category_id = Column(Integer, ForeignKey('bill_sub_category.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User')
    bill_sub_category = relationship('BillSubCategory')

    def __repr__(self):
        return self.bill_sub_category.name








