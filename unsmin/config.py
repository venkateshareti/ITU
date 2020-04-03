import os

# postgres_local_base = os.environ['DATABASE_URL']

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False
    LOG_FORMAT = (
        '[%(asctime)s] %(levelname)s in %(filename)s:%(lineno)d '
        '%(message)s')
    PAGINATION_SEARCH_COUNT = 3

class StagingConfig(Config):
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGIN_URL = "https://unsmin.dss.un.org/Login-Registration/UNSMIN-Login?returnurl=%2f"
    PROFILE_X_RAY_URL = "https://unsmin.dss.un.org/TRIP/Profile-X-ray"
    REPORT_URL = "https://unsmin.dss.un.org/Reports"
    USERNAME = "thierry.zaradez@itu.int"
    PASSWORD = "ITUduringdev-4321"


class DevelopmentConfig(Config):
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base


config_by_name = dict(
    stag=StagingConfig,
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY