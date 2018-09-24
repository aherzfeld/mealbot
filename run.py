from mealbot_app import app, db
from mealbot_app.models import User


# this creates a shell context that adds the database instance and models to the shell session
# just run 'flask shell' to initiate the context
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}
