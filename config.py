from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


SQLALCHEMY_TRACK_MODIFICATIONS: bool = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', False) == 'True'
SQLALCHEMY_DATABASE_URI: str = environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
SECRET_KEY: str = environ.get('SECRET_KEY')
JWT_SECRET_KEY: str = environ.get('JWT_SECRET_KEY')
AWS_ACCESS_KEY_ID: str = environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY: str = environ.get('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME: str = environ.get('AWS_BUCKET_NAME')
PRODUCTION_MODE: bool = environ.get('PRODUCTION_MODE', False) == 'True'
