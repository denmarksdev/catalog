# To generate  CSRF protection
import random
import string
# Flask
from flask import session as login_session
from flask import request, json, make_response
from config import APP_ROOT

# Authentication systems
BASIC_PROVIDER = "basic"
GOOGLE_PROVIDER = "google"
FACEBOOK_PROVIDER = "facebook"


def set_base_login_session(user, provider):
    """
    Defines the common information of a session, 
    based on authentication system (provider)
    """
    login_session['provider'] = provider
    login_session['user_id'] = user.id
    login_session['username'] = user.name
    login_session['picture'] = user.picture
    login_session['email'] = user.username


def is_logged():
    return 'username' in login_session


def get_user_name():
    if (is_logged):
        return login_session['username']
    return "User note logged"


def is_item_owner(user_id):
    return is_logged() and login_session['user_id'] == user_id


def is_invalid_state_token():
    return (request.args.get('state') != login_session['STATE'])


def create_invalid_state_response():
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response


# To prevents cross-site request forgery attack
def generate_CSRF_token():
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for x in xrange(32))
