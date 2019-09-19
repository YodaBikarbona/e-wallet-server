from flask import Flask
#from flask.ext.scss import Scss
import os
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# ----- Config -----
app = Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mihael:Mihael0110.@localhost/e_wallet?use_unicode=1&charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Flask

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

app.config.from_pyfile('config.cfg')
mail = Mail(app)
#Scss(app)
