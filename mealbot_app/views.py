from mealbot_app import app
from flask import render_template


@app.route("/")
def index():
    #return "hello, world"
    return render_template("index.html")
