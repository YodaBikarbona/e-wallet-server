from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, Unicode, Column, Date, Float
from sqlalchemy.orm import relationship
from api.helper.helper import now
from api.model.config import db
from api.model.user import User


class Bugs(db.Model):
    __tablename__ = 'bugs'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    comment = Column(Unicode(255), nullable=False)
    is_fixed = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User')

    def __repr__(self):
        return self.title
