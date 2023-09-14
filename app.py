from flask import Flask, render_template, redirect, session, flask
from flask_debugtoolbar import DebugToolbarExtension
from mdoels import connect_db, db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hashing_login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route("/")
def homepage():
    """Show homepage with links to site areas."""

    return "Test"

@app.route("/register", methods = ["GET","POST"])
def register():
    """Register a User: Display form & handle submission"""

