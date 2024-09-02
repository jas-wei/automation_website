from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

import os


db = SQLAlchemy() # object used to manipulate database
DB_NAME = "other_other_database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'alksnfgsdohuinwel69023nosg'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # telling to store database in website folder

    UPLOAD_FOLDER = os.path.join('website', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Set 'UPLOAD_FOLDER' key in app config

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .models import User, Preferences

    # url_prefix is starting character of each route ('/' is default)
    app.register_blueprint(views, url_prefix='/') 
    app.register_blueprint(auth, url_prefix='/')
    
    
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' #where to redirect if user not logged in (change)
    login_manager.init_app(app) #tell which app were using

    #tell flask which user to look for
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    '''
    Create a database for this app.
    '''
    if not path.exists('website/' + DB_NAME): # if there doesn't already exist a database for this app
        with app.app_context():
            db.create_all() # create database tables
        print('Created Database!')

