"""
Module to contain basic config for the module
"""
import os
from datetime import datetime
import pytz
import yaml

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class Config:
    """
    Config for the database connection and the db configuration
    """
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'pretend this is from a secrets manager'
    sort_keys = False
    db_config = yaml.full_load(open('app/db.yml', encoding="utf-8"))
    base_str = "mysql+pymysql://"
    user_str = db_config['mysql_user']
    password_str = db_config['mysql_password']
    host_str = db_config['mysql_host']
    db_str = db_config['mysql_db']
    SQLALCHEMY_DATABASE_URI = f"{base_str}{user_str}:{password_str}@{host_str}/{db_str}"


def current_datetime(kind: str):
    """
    Simple function to get todays datetime in either string or datetime formatted as 2024-07-17T16:11:09
    """
    if kind == 'string':
        return datetime.now(pytz.timezone('Eire')).strftime(DATETIME_FORMAT)
    else:
        return datetime.strptime(datetime.now(pytz.timezone('Eire')).strftime(DATETIME_FORMAT), DATETIME_FORMAT)
