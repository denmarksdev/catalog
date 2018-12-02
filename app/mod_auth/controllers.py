# Import flask dependencies
from flask import Blueprint, request, render_template, \
    flash, g, session, redirect, url_for

from app.mod_auth.models import User

# Import module forms
from app.mod_auth.forms import LoginForm, SignupForm

# Define the blueprint: 'catalog', set its url prefix: app.url/catalog
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')


# Interaction with user entity of the database
from app.mod_auth.repositories import UserRepository

# Helpers to set login session common information
from app.mod_auth.helpers import set_base_login_session, \
    login_session, generate_CSRF_token, BASIC_PROVIDER

from app import db


@mod_auth.route('/login', methods=['GET', 'POST'])
def show_signin():
     # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():
        repo = UserRepository(db.session)
        user = repo.find_by_username(form.username.data)
        if (user and user.verify_password(form.password.data)):
            set_base_login_session(user,  BASIC_PROVIDER)
            return redirect(url_for('index'))
        else:
            flash('User or password is invalid!')

    # Anti Cross-site request forgery token
    state = generate_CSRF_token()
    login_session['STATE'] = state

    return render_template("auth/signin.html",
                           form=form,
                           STATE=state)


@mod_auth.route('/signup', methods=['GET', 'POST'])
def show_signup():
    # If signup in form is submitted
    form = SignupForm(request.form)

    # Verify the signup in form
    if form.validate_on_submit():
        try:
            repo = UserRepository(db.session)
            if repo.has_by_username(form.name.data):
                flash('Username is already registered')
            else:  # Persist user and redirect to catalog page
                user = User()
                user.name = form.name.data
                user.username = form.username.data
                user.hash_password(form.password.data)
                repo.add(user)
                repo.commit()
                return redirect(url_for('index'))
        except:
            flash('Fail save user in database :(')

    return render_template("auth/signup.html", form=form)
