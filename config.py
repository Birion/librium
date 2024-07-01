"""Flask config."""
from os import environ, path
from dotenv import find_dotenv, load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(find_dotenv())


class Config:
    """Base config."""
    SECRET_KEY = environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME")


class ProdConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False


class DevConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True
