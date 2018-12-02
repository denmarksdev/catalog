from flask import Blueprint, make_response, jsonify, \
    redirect, url_for, request, json
from flask_restful import Resource, Api
# Google Connect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests
# Application
from config import API_URL, APP_ROOT
from app import db
from app.mod_auth.models import User
from app.mod_auth.repositories import UserRepository
from app.mod_auth.helpers import login_session, \
    is_invalid_state_token, create_invalid_state_response, \
    set_base_login_session
from app.mod_auth.helpers import GOOGLE_PROVIDER, \
    FACEBOOK_PROVIDER
# Google Client ID
GOOGLE_CLIENT_ID = json.loads(open(APP_ROOT + '/secrets_google.json', 'r').read())[
    'web']['client_id']
# Create Blueprint
api_controller = Blueprint('api_auth',
                           __name__,
                           url_prefix=API_URL + '/auth')
# Link an Api up to a Blueprint.
api = Api(api_controller)


class Logout(Resource):
    def post(self):
        if 'provider' in login_session:
            if (login_session['provider'] == GOOGLE_PROVIDER):
                googledisconnect
            if (login_session['provider'] == FACEBOOK_PROVIDER):
                fbdisconnect()

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        return redirect(url_for('catalog.show'))

# GOOGLE AUTH


class GooggleConnect(Resource):
    def post(self):
        """
        Get Google Sign In API and places it inside a session variable.
        """
        if is_invalid_state_token():
            return create_invalid_state_response()

        # Obtain authorization code
        code = request.data

        try:
            screts_json = APP_ROOT + "/secrets_google.json"

            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(screts_json, scope='')
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
        if result['issued_to'] != GOOGLE_CLIENT_ID:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            print "Token's client ID does not match app's."
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_access_token = login_session.get('access_token')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is connected.'),
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

        repo = UserRepository(db.session)
        user = repo.find_by_username(login_session['email'])
        if (user is None):
            user_id = createUser(repo)
        else:
            user_id = user.id

        login_session['user_id'] = user_id

        output = ''
        output += '<h1>Welcome, '
        output += login_session['username']
        output += '!</h1>'
        output += '<img src="'
        output += login_session['picture']
        output += """
        " style = "width: 300px; height: 300px;border-radius: 150px;
        -webkit-border-radius: 150px;-moz-border-radius: 150px;">
        """

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
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# FACEBOOK AUTH


class FacebookConnect(Resource):

    def post(self):
        """
        Get Facebook Sign In API and places it inside a session variable.
        """
        if is_invalid_state_token():
            return create_invalid_state_response()

        access_token = request.data

        secrets_path = APP_ROOT + '/secrets_facebook.json'

        app_id = json.loads(open(secrets_path, 'r').read())[
            'web']['app_id']
        app_secret = json.loads(open(secrets_path, 'r').read())[
            'web']['app_secret']

        url = ('https://graph.facebook.com/oauth/access_token?'
               'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
               '&fb_exchange_token=%s' % (app_id, app_secret, access_token))

        h = httplib2.Http()
        result = h.request(url, 'GET')[1]

        userinfo_url = "https://graph.facebook.com/v3.2/me"

        token = result.split(',')[0].split(':')[1].replace('"', '')

        url = ('https://graph.facebook.com/v3.2/me?' +
               'fields=name,id,email&access_token=%s' % token)

        url = url.replace(',', '%2C')

        h = httplib2.Http()
        result = h.request(url, 'GET')[1]

        data = json.loads(result)
        print(data)

        login_session["provider"] = FACEBOOK_PROVIDER
        login_session["username"] = data["name"]
        login_session["email"] = data["email"]
        login_session["facebook_id"] = data["id"]

        # Get user picture
        url = ('https://graph.facebook.com/v3.2/me/picture' +
               '?access_token=%s&redirect=0&height=200&width=200'
               % token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        data = json.loads(result)

        login_session['picture'] = data["data"]["url"]

        # see if iser exists

        repo = UserRepository(db.session)
        user = repo.find_by_username((login_session['email']))
        if not user:
            user_id = createUser(repo)
        else:
            user_id = user.id

        login_session['user_id'] = user_id

        output = ''
        output += '<h1>Welcome, '
        output += login_session['username']
        output += '!</h1>'
        output += '<img src="'
        output += login_session['picture']
        output += """
        " style = "width: 300px; height: 300px;border-radius: 150px;
        -webkit-border-radius: 150px;-moz-border-radius: 150px;">
        """
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


# Register apis on blueprint
api.add_resource(GooggleConnect, '/gconnect')
api.add_resource(FacebookConnect, '/fbconnect')
api.add_resource(Logout, '/logout')

# Auxliary functions


def createUser(repo):
    newUser = User(name=login_session['username'],
                   username=login_session['email'],
                   picture=login_session['picture'])
    repo.add(newUser)
    repo.commit()
    user = repo.find_by_username(login_session['email'])
    return user.id
