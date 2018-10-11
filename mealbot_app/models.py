from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from time import time
from mealbot_app import app, db, login
from flask_login import UserMixin
import jwt


liked_recipes = db.Table('liked_recipes',
    db.Column('liker_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    added_recipes = db.relationship(
        'Recipe', backref='added_by', lazy='dynamic')
    recipes = db.relationship(
        'Recipe', secondary=liked_recipes,
        backref=db.backref('likers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def like_recipe(self, recipe):
        if not self.likes_recipe(recipe):
            self.recipes.append(recipe)

    def unlike_recipe(self, recipe):
        if self.likes_recipe(recipe):
            self.recipes.remove(recipe)

    def likes_recipe(self, recipe):
        return self.recipes.filter(
            liked_recipes.c.recipe_id == recipe.id).count() > 0

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        # blank return returns None (to prevent error is token fails)
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)


# this helps flask-login load the user from session
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_json = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(60), unique=True)
    url = db.Column(db.String(200), unique=True)
    image_url = db.Column(db.String(200))
    rdy_in_minutes = db.Column(db.Integer)
    servings = db.Column(db.Integer)
    ingredients = db.Column(db.ARRAY(db.String))
    steps = db.Column(db.ARRAY(db.String))

    def __repr__(self):
        return 'Added by: {}, \n{}'.format(self.added_by, self.recipe_json)



