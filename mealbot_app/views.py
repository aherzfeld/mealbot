import json
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from mealbot_app import app, db
from mealbot_app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from mealbot_app.models import User, Recipe
from mealbot_app.forms import ResetPasswordRequestForm, ResetPasswordForm, \
    GetRecipeForm, MealPlannerForm
from mealbot_app.email import send_password_reset_email
# import our spoonacular API wrapper package
import spoonacular as sp
# Create our spoonacular API class
sp_api = sp.API(app.config["SP_API_KEY"])


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/addmeal', methods=['GET', 'POST'])
# this will redirect to /login along with query string URL arg so the user will be redirected to the page they wanted prior to login
@login_required
def addmeal():
    form = GetRecipeForm()
    if form.validate_on_submit():
        # use api method to check api call limit first
        recipe = Recipe.query.filter_by(url=form.url.data).first()
        if recipe:
            current_user.like_recipe(recipe)
            db.session.commit()
            return redirect(url_for('recipe', title=recipe.title))
        response = sp_api.extract_recipe_from_website(form.url.data)
        if response is None:
            flash("Sorry, we were unable to extract your recipe's data.")
            return redirect(url_for('addmeal'))
        data = response.json()
        with open(
                'mealbot_app/recipes_json/' + data['title'] +
                '.json', 'w') as outfile:
            json.dump(data, outfile, indent=2)  # not tested yet
        ingredients = []  # create for loop to extract ingredients
        for item in data['extendedIngredients']:
            ingredients.append(item['originalString'])
        steps = []
        for item in data['analyzedInstructions'][0]['steps']:
            steps.append(item['step'])
        print(ingredients, steps)  # for testing
        recipe = Recipe(added_by=current_user, title=data['title'],
                        url=data['sourceUrl'], image_url=data['image'],
                        rdy_in_minutes=data['readyInMinutes'],
                        servings=data['servings'], ingredients=ingredients,
                        steps=steps)
        current_user.like_recipe(recipe)
        db.session.add(recipe)
        db.session.commit()
        flash("You're new recipe was succesfully added!")
        return redirect(url_for('recipe', title=recipe.title))
    return render_template('addmeal.html', title='Add Meal', form=form)


@app.route('/recipe/<title>')  # recipe=title
@login_required
def recipe(title):  # maybe i should send recipe as an arg as well
    recipe = Recipe.query.filter_by(title=title).first_or_404()
    return render_template('recipe.html', recipe=recipe)


@app.route('/explore')
@login_required
def explore():
    recipes = Recipe.query.order_by(Recipe.id.desc()).all()
    return render_template('explore.html', title='Explore', recipes=recipes)


@app.route('/meals')
@login_required
def meals():
    recipes = current_user.recipes
    return render_template('meals.html', recipes=recipes)


@app.route('/mealplanner', methods=['GET', 'POST'])
@login_required
def mealplanner():
    form = MealPlannerForm()
    if form.validate_on_submit():
        redirect(url_for('mealplanner'))  # temporary placeholder
    return render_template('mealplanner.html', title='Meal Planner', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()  # instantiates form object
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are registered!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)








