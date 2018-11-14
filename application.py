#!/usr/bin/env python2

from flask import Flask, redirect, url_for
from data.data_access import create_sample_data
from controllers.api_controller import api_controller
from controllers.auth_controller import (auth_controller, auth_pages,
                                         is_logged, get_user_name)
from controllers.catalog_controller import catalog_controller

app = Flask(__name__)

# Initialize application routes
app.register_blueprint(auth_controller)
app.register_blueprint(auth_pages)
app.register_blueprint(catalog_controller)
app.register_blueprint(api_controller)


@app.route('/')
def main_route():
    return redirect(url_for('catalog.show_catalog'))


@app.context_processor
def utility_processor():
    """
    Global functions, use in Jinja2 templates.
    """
    def user_is_logged():
        return is_logged()

    def get_welcome_user():
        return get_user_name()

    return dict(user_is_logged=user_is_logged,
                get_welcome_user=get_welcome_user)


if __name__ == '__main__':

    create_sample_data()

    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
