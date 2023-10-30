import logging
from logging import config
from settings import LOGGER_CONF_PATH


config.fileConfig(LOGGER_CONF_PATH)

def get_logger(logger_name:str='root')-> logging.Logger:
    return logging.getLogger(logger_name)