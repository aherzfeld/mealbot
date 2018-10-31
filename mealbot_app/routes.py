import json
from datetime import datetime
from sqlalchemy import func  # for mealplanner
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from mealbot_app import app, db
from mealbot_app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from mealbot_app.models import User, Recipe
from mealbot_app.forms import ResetPasswordRequestForm, ResetPasswordForm, \
    GetRecipeForm, MealPlannerForm, EditProfileForm
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
        # use api method to check api call limit first (built in)
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
        # shut down for heroku deployment
        #with open(
        #        'mealbot_app/recipes_json/' + data['title'] +
        #        '.json', 'w') as outfile:
        #    json.dump(data, outfile, indent=2)
        # temporarily filter out non-spoonacular recipes
        #if data['id'] < 1:
        #    flash("Sorry, we were unable to extract your recipe's data.")
        #    return redirect(url_for('addmeal'))
        ingredients = []
        # check if ingredients were extracted successfully
        if data['extendedIngredients']:
            for item in data['extendedIngredients']:
                # confirm that item is a food in spoonacular's db
                if item['id']:
                    ingredients.append(item['originalString'])
        steps = []
        # check if steps were extracted successfully
        if data['analyzedInstructions']:
            for item in data['analyzedInstructions'][0]['steps']:
                if len(str(item['step'])) > 3:
                    steps.append(item['step'])
        print(ingredients, steps)  # for testing
        # filter out incomplete recipes
        if not ingredients or not steps:
            flash("Sorry, we were unable to extract your recipe's data.")
            return redirect(url_for('addmeal'))
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


@app.route('/recipe/<title>')
@login_required
def recipe(title):
    recipe = Recipe.query.filter_by(title=title).first_or_404()
    return render_template('recipe.html', recipe=recipe)


@app.route('/like/<title>')
@login_required
def like_recipe(title):
    recipe = Recipe.query.filter_by(title=title).first()
    if recipe is None:
        flash('Recipe {} not found.'.format(title))
        return redirect(url_for('index'))
    current_user.like_recipe(recipe)
    db.session.commit()
    flash('You have added {} to your meals!'.format(title))
    return redirect(url_for('recipe', title=title, recipe=recipe))


@app.route('/unlike/<title>')
@login_required
def unlike_recipe(title):
    recipe = Recipe.query.filter_by(title=title).first()
    if recipe is None:
        flash('Recipe {} not found.'.format(title))
        return redirect(url_for('index'))
    current_user.unlike_recipe(recipe)
    db.session.commit()
    flash('You have removed {} from your meals!'.format(title))
    return redirect(url_for('recipe', title=title, recipe=recipe))


@app.route('/explore')
@login_required
def explore():
    recipes = Recipe.query.order_by(Recipe.id.desc()).all()
    return render_template('explore.html', title='Explore', recipes=recipes)


@app.route('/meals')
@login_required
def meals():
    recipes = current_user.recipes
    if len(recipes.all()) < 1:
            flash("You don't have any meals yet!")
            return render_template('meals.html')
    return render_template('meals.html', recipes=recipes)


@app.route('/mealplanner', methods=['GET', 'POST'])
@login_required
def mealplanner():
    form = MealPlannerForm()
    if form.validate_on_submit():
        # query users recipes and select n randomly
        recipes = current_user.recipes.order_by(
            func.random()).limit(form.num_meals.data)
        if len(recipes.all()) < 1:
            flash("You don't have any meals yet!")
            return redirect(url_for('mealplanner'))
        return render_template('mealplanner.html', title='Meal Planner',
                               form=form, recipes=recipes)
    return render_template('mealplanner.html', title='Meal Planner', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    recipes = user.recipes
    recipes_added = len(user.added_recipes.all())
    if len(user.recipes.all()) < 1:
        return render_template('user.html', title="Profile", user=user)
    return render_template('user.html', title="Profile", user=user,
                           recipes=recipes, recipes_added=recipes_added)


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
        user = User(username=form.username.data, email=form.email.data,
                    user_created=datetime.utcnow())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are registered!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


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


# this flask decorator causes this function to execute before any view function
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()






