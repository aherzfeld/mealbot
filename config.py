import os
from dotenv import load_dotenv


# see part 4 flask-Mega to see usage of import os / os.path.dirname
basedir = os.path.abspath(os.path.dirname(__file__))
# import .env before Config is created so variables are set when it is
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # username and password optional (if not localhost)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # list of admin email addresses
    ADMINS = ['herzfeld.andrew@gmail.com']
    # database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # spoonacular api
    SP_API_KEY = os.environ.get('SP_API_KEY')
    # for Heroku
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
