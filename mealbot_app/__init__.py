from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
# this will load secret keys from instance/config.py
app.config.from_pyfile('config.py')

import mealbot_app.views