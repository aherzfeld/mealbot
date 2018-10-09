from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
# this will load secret keys from instance/config.py
app.config.from_pyfile('config.py')
# instantiate our db with SQLAlchemy
db = SQLAlchemy(app)
# instantiate our migration engine - part 4 flask mega tutorial
migrate = Migrate(app, db)
login = LoginManager(app)
# inform flask-login which function handles the logins to enable require login
login.login_view = 'login'
mail = Mail(app)
bootstrap = Bootstrap(app)

from mealbot_app import views, models