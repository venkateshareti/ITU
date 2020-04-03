import logging
from unsmin.config import Config
from typing import Type


def get_custom_formatter(config: Type[Config]) -> logging.Formatter:
    return logging.Formatter(config.LOG_FORMAT)


# import logging
# from logging.handlers import RotatingFileHandler
# log = logging.getLogger('urllib3')  # works to get https connections
# log.setLevel(logging.DEBUG)  # needed to set looger level
# formatter_api = logging.Formatter("[%(asctime)s]  %(levelname)s - %(message)s")  # logger format
# fh = RotatingFileHandler("./dayforce/logger_details/logger_info.log", mode='a', maxBytes=5*1024*1024,
#                                  backupCount=2, encoding=None, delay=0)  # logger filehandle to save in particular file
# fh.setFormatter(formatter_api)  # set the format to logger
# log.addHandler(fh)  # adding the handler to logger