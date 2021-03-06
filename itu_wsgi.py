#! /usr/bin/python3.6

import os
import sys

python_home = '/opt/ituflask/ituvenv'
from unsmin.config import basedir
sys.path.insert(0, '/opt/ituflask/ITU_ENV/ITU')

#activate_this = '/opt/ituflask/ituvenv/bin/activate_this.py'
#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))

config_name = os.environ['FLASK_ENV']

from unsmin.app import create_app

application = create_app(config_name)
