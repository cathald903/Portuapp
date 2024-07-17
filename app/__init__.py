"""
init file
"""
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    """
    Intialises the application by reading in database config and opening the connection
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    bcrypt = Bcrypt(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # get db connection
    from app.database import init_db, import_from_csv
    with app.app_context():
        init_db()

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
