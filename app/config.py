import os
import pytz
import yaml
from datetime import datetime


class Config:
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


datetime_format = '%Y-%m-%dT%H:%M:%S'


def current_datetime(kind: str):
    if kind == 'string':
        return datetime.now(pytz.timezone('Eire')).strftime(datetime_format)
    else:
        return datetime.strptime(datetime.now(pytz.timezone('Eire')).strftime(datetime_format), datetime_format)
