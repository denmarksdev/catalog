from flask import Blueprint, render_template, make_response, request, redirect, url_for, json, jsonify, flash
from data.database_setup import User
from data.data_access import UserDao
from constants import BASE_API_URL, IMAGE_PATH
# ANTI-FORGERY STATE TOKEN
from flask import session as login_session
import random
import string
# Google Connect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
# Basic Auth
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

# Google Client ID
CLIENT_ID = json.loads(open('secrets_google.json', 'r').read())[
    'web']['client_id']

# Auth providers
GOOGLE_PROVIDER = "google"
FACEBOOK_PROVIDER = "facebook"
BASIC_PROVIDER = "basic"

# Create controller
auth_controller = Blueprint("auth_controller",
                            __name__,
                            url_prefix=BASE_API_URL)

auth_pages = Blueprint("auth_controller_pages",
                       __name__,
                       template_folder='templates')

# Views pages


@auth_pages.route('/login')
def show_login():
    state = generate_anty_forgery_state_token()
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@auth_pages.route('/signup', methods=['GET', 'POST'])
def show_signup_form():
    user = User()

    if (request.method == 'GET'):
        state = generate_anty_forgery_state_token()
        login_session['state'] = state
        return render_template('signup.html', user=user, STATE=state)
    else:  # POST

        if request.form['state'] != login_session['state']:
            return create_invalid_state_response()

        user_dao = UserDao()

        user.name = request.form['name']
        user.username = request.form['username']
        user.password = request.form['password']
        confirm_password = request.form['confirmPassword']

        if (not validate_user(user, confirm_password, user_dao)):
            state = generate_anty_forgery_state_token()
            return redirect(url_for('auth_controller_pages.show_signup_form'))

        user.hash_password(user.password)
        # TODO: Save image user from form-data.
        user.picture = IMAGE_PATH + "default.png"
        try:
            user_dao.save(user)
        except:
            return make_response("Failed to save user data", 500)
        return redirect(url_for('auth_controller_pages.show_login'))


def validate_user(user, confirm_password, user_dao):
    if not user.name:
        flash("User name is empty")
        return False
    elif not user.password:
        flash("User password is empty")
        return False
    elif not confirm_password:
        flash("User Confirm Passsoword is empty")
        return False
    elif (user.password != confirm_password):
        flash("password and confirm password are different")
        return False
    elif(user_dao.has_by_username(user.username)):
        flash(" 'Username is already registered'")
        return False

    return True

# Endpoints


@auth_controller.route("/auth/logout", methods=['POST'])
def logout():
    if 'provider' in login_session:
        if (login_session['provider'] == GOOGLE_PROVIDER):
            googledisconnect()
        if (login_session['provider'] == FACEBOOK_PROVIDER):
            fbdisconnect()

    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    return redirect(url_for('catalog.show_catalog'))


@auth_controller.route("/auth/gconnect", methods=["POST"])
def googleconnect():
    """
     Gathers data from Google Sign In API and places it inside a session variable.
    """

    if is_valid_state_token():
        return create_invalid_state_response()

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('secrets_google.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print("googleconnect")

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    dao = UserDao()

    user = dao.find_by_username(login_session['email'])
    if (user is None):
        user_id = createUser(dao)
    else:
        user_id = user.id

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    print "done!"
    print(output)
    return output


def googledisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# FACEBOOK OAUTH2


@auth_controller.route('/auth/fbconnect', methods=['POST'])
def fbconnecty():
    if is_valid_state_token():
        return create_invalid_state_response()

    access_token = request.data

    app_id = json.loads(open('secrets_facebook.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(open('secrets_facebook.json', 'r').read())[
        'web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    userinfo_url = "https://graph.facebook.com/v3.2/me"

    # curl -i -X GET \
    # "https://graph.facebook.com/v3.2/me?fields=id%2Cname&access_token=EAAXG8evn8rsBAJ0R5wOtbKllg6Yc6DKKAAOEF10ekf0tALjgZCfo4q6docPr3T6IsePuimVAQAo7FmqpBGRwmP1sdVZB3AAFBkZCqDLZBdhHCIXZAr2OtxQVEOk0EQOvBZCcDZAP7m9P8h8QAwlcgQyDECB1YRFgHKjxx551ERCgSslaB5JZClSieTgVlQkm12QZD"

    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v3.2/me?fields=name,id,email&access_token=%s' % token

    url = url.replace(',', '%2C')

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    print(data['name'])

    login_session["provider"] = FACEBOOK_PROVIDER
    login_session["username"] = data["name"]
    login_session["email"] = data["email"]
    login_session["facebook_id"] = data["id"]

    # Get user picture
    url = 'https://graph.facebook.com/v3.2/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if iser exists

    user_dao = UserDao()
    user = user_dao.find_by_username((login_session['email']))
    if not user:
        user_id = createUser(user_dao)
    else:
        user_id = user.id

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    print(output)
    return output


def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    del login_session['facebook_id']
    return "you have been logged out"


# BASIC AUTH

@auth.verify_password
def verify_password(username, password):

    if is_valid_state_token():
        return create_invalid_state_response()

    user_dao = UserDao()
    user = user_dao.find_by_username(username)
    if not user or not user.verify_password(password):
        return False
    if is_logged():
        return True
    login_session['provider'] = 'basic_auth'
    login_session['user_id'] = user.id
    login_session['username'] = user.name
    login_session['picture'] = user.picture
    login_session['email'] = user.username
    return True


@auth_controller.route("/auth/basic", methods=["POST"])
@auth.login_required
def local_permission_connect():
    return make_response("OK", 200)

# Auxliary functions


def createUser(dao):
    newUser = User(name=login_session['username'],
                   username=login_session['email'],
                   picture=login_session['picture'])
    dao.save(newUser)
    user = dao.find_by_username(login_session['email'])
    return user.id


def is_logged():
    return 'username' in login_session


def get_user_name():
    if (is_logged):
        return login_session['username']
    return "User note logged"


def generate_anty_forgery_state_token():
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for x in xrange(32))


def is_valid_state_token():
    return (request.args.get('state') != login_session['state'])


def create_invalid_state_response():
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    print(request.args.get('state'))
    return response
