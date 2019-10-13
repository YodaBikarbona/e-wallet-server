from flask import Flask
#from flask.ext.scss import Scss
import os
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# ----- Config -----
app = Flask(__name__, static_url_path='')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mihael:Mihael0110.@localhost/e_wallet?use_unicode=1&charset=utf8mb4'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Mihael:Mihael0110.@localhost:5432/e_wallet'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nuunnhgldwiswb:d3786174762426b0f7516ab5679e88144b4e9c16bb9b37582c866461b5d1d635@ec2-54-217-225-16.eu-west-1.compute.amazonaws.com:5432/deomvf9srj5c3d'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Flask

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

app.config.from_pyfile('config.cfg')
mail = Mail(app)
#Scss(app)


