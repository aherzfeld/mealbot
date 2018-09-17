from flask import Flask
from flask import render_template


app = Flask('mealbot_app')
app.config.from_object('config')

