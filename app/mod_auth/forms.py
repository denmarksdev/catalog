# Import Form 
from flask_wtf import FlaskForm 

# Import Form elements such as TextField, PasswordField and SelectField
from wtforms import TextField, PasswordField

# Import Form validators
from wtforms.validators import Required, EqualTo


class LoginForm(FlaskForm):
    """
        Define the login form (WTForms)
    """
    username = TextField('User name', [
        Required(message='Forgot your user name?')])
    password = PasswordField('Password', [
        Required(message='Must provide a password. ;-)')])


class SignupForm(FlaskForm):
    """
        Define the Signup form (WTForms)
    """
    name = TextField('Name', [
        Required(message='Forgot your name?')])
    username = TextField('User name', [
        Required(message='Forgot your user name?')])
    password = PasswordField('Password', [
        Required(message='Must provide a password. ;-)')])
    password_confirm = PasswordField('Comfirm password', [
        EqualTo('password', message='Passwords must match'),
        Required(message='Must provide a confimr password. ;-)')
    ])
