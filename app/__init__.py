#!/usr/bin/env python

# Import flask and template operators
from flask import Flask, render_template, redirect, url_for

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy


# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)


# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_auth.api import api_controller as auth_api
from app.mod_catalog.controllers import mod_catalog as catalog_module
from app.mod_catalog.api import api_controller as catalog_api
import app.mod_auth.helpers as auth_helper

# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(catalog_module)
app.register_blueprint(catalog_api)
app.register_blueprint(auth_api)


@app.route('/')
def index():
    return redirect(url_for('catalog.show'))


@app.context_processor
def utility_processor():
    """
    Global functions, use in Jinja2 templates.
    These functions are ensuring that the user name is updated correctly 
    on header of page.
    """
    def user_is_logged():
        return auth_helper.is_logged()

    def get_welcome_user():
        return auth_helper.get_user_name()

    return dict(user_is_logged=user_is_logged,
                get_welcome_user=get_welcome_user)
