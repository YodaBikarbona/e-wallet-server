from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, Unicode, Column, Date, Float
from sqlalchemy.orm import relationship
from api.helper.helper import now, new_salt, new_psw
from api.model.config import db
from api.model.country import Country, Currency, City


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    first_name = Column(Unicode(255), nullable=False)
    last_name = Column(Unicode(255), nullable=False)
    email = Column(Unicode(255), unique=True, nullable=False)
    activated = Column(Boolean, default=False)
    password = Column(Unicode(255), nullable=False)
    salt = Column(Unicode(255), nullable=False)
    first_login = Column(DateTime, default=now())
    last_login = Column(DateTime, default=now())
    birth_date = Column(Date, nullable=False)
    gender = Column(Unicode(255), nullable=False)
    address = Column(Unicode(255), nullable=False)
    phone = Column(Unicode(255), nullable=True, default='')
    new_password_code = Column(Unicode(6), nullable=True)
    new_password_code_expired = Column(DateTime, nullable=True)
    code = Column(Unicode(6), nullable=True)
    application_rating = Column(Integer, nullable=0)

    city_id = Column(Integer, ForeignKey('city.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
    image_id = Column(Integer, ForeignKey('image.id', ondelete='CASCADE'), nullable=True)
    country_id = Column(Integer, ForeignKey('country.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('currency.id', ondelete='CASCADE'), nullable=True)

    role = relationship('Role')
    image = relationship('Image')
    country = relationship('Country')
    currency = relationship('Currency')
    city = relationship('City')

    def __repr__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def set_salt(self):
        self.salt = new_salt()

    def set_psw(self):
        self.password = new_psw(self.salt, self.password)


class Role(db.Model):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    role_name = Column(Unicode(255), nullable=False)

    def __repr__(self):
        return '{0}'.format(self.role_name)


class Image(db.Model):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    type = Column(Unicode(255))
    name = Column(Unicode(255))
    file_name = Column(Unicode(255))

    def __repr__(self):
        return '{0}'.format(self.file_name)


class UserCurrency(db.Model):
    __tablename__ = 'user_currency'

    id = Column(Integer, primary_key=True)
    monthly_cost_limit = Column(Float, default=1000)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    currency_id = Column(Integer, ForeignKey('currency.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User')
    currency = relationship('Currency')

    def __repr__(self):
        return self.code


class News(db.Model):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    title = Column(Unicode(255), nullable=False)
    content = Column(Unicode(255), nullable=False)
    type = Column(Unicode(255), nullable=False)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User')

    def __repr__(self):
        return self.title


class UserNews(db.Model):
    __tablename__ = 'user_news'

    id = Column(Integer, primary_key=True)
    positive_choice = Column(Boolean)
    hidden = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    news_id = Column(Integer, ForeignKey('news.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User')
    news = relationship('News')

    def __repr__(self):
        return self.title

