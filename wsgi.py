import os

from unsmin.config import basedir

config_name = os.environ['FLASK_ENV']

from unsmin.app import create_app

app = create_app(config_name)
