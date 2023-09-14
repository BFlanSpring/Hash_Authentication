from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired


class RegisterForm(FlaskForm):
    """Form for regestering a user"""

    username = StringField("Username", validators = [InputRequired()])
    password = PasswordField("Password", validators = [InputRequired()])

class LoginForm(FlaskForm):
    """Form for logging in a user"""

    username = StringField ("Username", validators = [InputRequired()])
    password = StringField ("Password", validators = [InputRequired()])