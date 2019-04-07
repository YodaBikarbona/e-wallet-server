from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, Unicode, Column, Date
from sqlalchemy.orm import relationship
from api.helper.helper import now, new_salt, new_psw
from api.model.config import db


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    deleted = Column(Boolean, default=False)
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
    city = Column(Unicode(255), nullable=False)
    change_mail = Column(Unicode(255), nullable=True, default='')
    key_word = Column(Unicode(255), nullable=True)
    state = Column(Unicode(255), nullable=False)
    code = Column(Unicode(6), nullable=True)

    role_id = Column(Integer, ForeignKey('role.id', ondelete='CASCADE'))
    image_id = Column(Integer, ForeignKey('image.id', ondelete='CASCADE'))

    role = relationship('Role')
    image = relationship('Image')

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
    deleted = Column(Boolean)
    role_name = Column(Unicode(255), nullable=False)

    def __repr__(self):
        return '{0}'.format(self.role_name)


class Image(db.Model):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=True, default=now())
    deleted = Column(Boolean)
    type = Column(Unicode(255))
    name = Column(Unicode(255))
    file_name = Column(Unicode(255))

    def __repr__(self):
        return '{0}'.format(self.file_name)
