from flask import render_template, flash, redirect, url_for
from mealbot_app import app
from mealbot_app.forms import LoginForm
# import our spoonacular API wrapper package
import spoonacular as sp
# Create our spoonacular API class
sp_api = sp.API(app.config["SP_API_KEY"])


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/addmeal')
def addmeal():
    return render_template('addmeal.html')


@app.route('/meals')
def meals():
    return render_template('meals.html')


@app.route('/mealplanner')
def mealplanner():
    return render_template('mealplanner.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # instantiates form object
    if form.validate_on_submit():
        # this is for testing before finishing login system
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)






