from flask import Flask, Blueprint
from flask_restful import Api
from .v1.test import hello
from .v1.profile_x_ray_data_access import data_search_and_access
from .v1.report_data import report_data
from .v1.middleware import Middleware
from unsmin.config import config_by_name
from .custom_log import get_custom_formatter
import logging

from .v1.custom_exceptions import errors
# from .v1.custom_exceptions import ApiError

ROOT_URL = '/ituapigw'


def create_app(config_name):

    config = config_by_name[config_name]
    app = Flask(__name__)
    app.config.from_object(config)

    app.config["APPLICATION_ROOT"] = ROOT_URL

    # from . import db
    # db.init_app(app)

    # set custom log format
    formatter = get_custom_formatter(config)
    app.logger.handlers[0].setFormatter(formatter)


    # Routes
    app.register_blueprint(hello, url_prefix='/Hello')
    app.register_blueprint(data_search_and_access, url_prefix=ROOT_URL)
    app.register_blueprint(report_data, url_prefix=ROOT_URL)

    app.wsgi_app = Middleware(app.wsgi_app)
    app.register_blueprint(errors)
    # app.errorhandler(ApiError)

    return app


