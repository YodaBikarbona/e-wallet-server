from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, Unicode, Column, Date
from sqlalchemy.orm import relationship
from api.helper.helper import now
from api.model.config import db


class Country(db.Model):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    name = Column(Unicode(255))
    phone_code = Column(Unicode(255))
    alpha2code = Column(Unicode(255))
    alpha3code = Column(Unicode(255))
    activated = Column(Boolean, default=False)

    def __repr__(self):
        return self.name


class City(db.Model):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    name = Column(Unicode(255))

    country_id = Column(Integer, ForeignKey('country.id', ondelete='CASCADE'), nullable=False)

    country = relationship('Country')

    def __repr__(self):
        return self.name


class Currency(db.Model):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    name = Column(Unicode(255))
    symbol = Column(Unicode(255))
    symbol_native = Column(Unicode(255))
    code = Column(Unicode(255))
    name_plural = Column(Unicode(255))
    activated = Column(Boolean, default=False)

    def __repr__(self):
        return self.code
