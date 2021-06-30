from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
SECRET_KEY = environ.get('SECRET_KEY')
JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = environ.get('AWS_BUCKET_NAME')