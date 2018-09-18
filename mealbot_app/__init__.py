from flask import Flask
# from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
# this will load secret keys from instance/config.py
app.config.from_pyfile('config.py')
# instantiate our db with SQLAlchemy
# db = SQLAlchemy(app)

import mealbot_app.views