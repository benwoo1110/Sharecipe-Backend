from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = environ.get('SECRET_KEY', 'some-secret-string')
JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
