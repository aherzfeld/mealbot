from mealbot_app import app
from flask import render_template


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/addmeal")
def addmeal():
    return render_template("addmeal.html")


@app.route("/meals")
def meals():
    return render_template("meals.html")


@app.route("/mealplanner")
def mealplanner():
    return render_template("mealplanner.html")
