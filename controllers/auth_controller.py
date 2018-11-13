from flask import Blueprint
from constants import BASE_API_URL, IMAGE_PATH
# Basic Auth
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

# Create controller
auth_controller = Blueprint("auth_controller",
                            __name__,
                            url_prefix=BASE_API_URL)

auth_pages = Blueprint("auth_controller_pages",
                       __name__,
                       template_folder='templates')
# View Pages


@auth_pages.route('/login')
def show_login():
    return "login page"


@auth_pages.route('/signup', methods=['GET', 'POST'])
def show_signup_form():
    return "signup form"


# Endpoints

@auth_controller.route("/auth/gconnect", methods=["POST"])
def logout():
    return "gconnect API"


@auth_controller.route("/auth/logout", methods=['POST'])
def google_connect():
    """
    Get Google API information and store information in session login
    """
    return "logout API"


@auth_controller.route('/auth/fbconnect', methods=['POST'])
def facebook_connect():
    """
    Get Facebook API information and store information in session login
    """
    return "gconnect API"


@auth_controller.route("/auth/basic", methods=["POST"])
@auth.login_required
def auth_basic_connect():
    """
    Get local user information and store information in session login
    """
    return "Auth basic API"

@auth.verify_password
def verify_password(username, password):
    return False
