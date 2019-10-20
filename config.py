from flask import Flask
#from flask.ext.scss import Scss
import os
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy.datamanager import ZopeTransactionExtension

# ----- Config -----
app = Flask(__name__, static_url_path='')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mihael:Mihael0110.@localhost/e_wallet?use_unicode=1&charset=utf8mb4'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Mihael:Mihael0110.@localhost:5432/e_wallet'


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ugftsmjcvosxdd:3d967a02c309165ebec9090710f7b62b9475b382a2e01fa5fceb27e6b673fb56@ec2-54-228-243-29.eu-west-1.compute.amazonaws.com:5432/d96bbod69lq3u7'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Flask

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

app.config.from_pyfile('config.cfg')
mail = Mail(app)
#Scss(app)


