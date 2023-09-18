from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hashing_login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

db.init_app(app)
connect_db(app)

if __name__ == "__main__":
    app.run(debug=True)
    

toolbar = DebugToolbarExtension(app)

@app.route("/", methods=["GET"])
def homepage():
    """Show homepage with links to site areas."""
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a User: Display form & handle submission"""
    form = RegisterForm()

    if form.validate_on_submit():
        # Get user input from the form
        username = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        # Create a new User object and add it to the database
        user = User.register(username, pwd, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        # Flash a success message and redirect to the homepage or a login page
        flash("User registered successfully!", "success")
        return redirect("/users/<username>")

    else:
        return render_template("register.html", form=form)

# @app.route("/login" methods=["GET","POST"])

@app.route("/login", methods=["GET","POST"])
def login():
    """shows login form and processes login for on submit"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        user = User.authenticate(username, pwd)

        if user:
            session["user_id"] = user.id
            return redirect(f"/users/{username}")  # Update the redirect URL
            
        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)




@app.route("/users/<username>", methods=["GET"])
def user_profile(username):
    """Display user profile information."""
    
    # Fetch the user from the database based on the provided username
    user = User.query.filter_by(username=username).first()

    if not user:
        # Handle the case where the user does not exist
        flash("User not found", "error")
        return redirect("/")  # Redirect to the homepage or an error page

    return render_template("user_profile.html", user=user)

@app.route("/logout")
def logout():
    """ Log out user by clearing session"""

    session.pop("user_id")

    return redirect("/")