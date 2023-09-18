from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

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
    return redirect("/login")

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
            session["username"] = user.username
            return redirect(f"/users/{username}")  # Update the redirect URL
            
        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)




@app.route("/users/<username>", methods=["GET"])
def user_profile(username):
    """Show information about the given user and their feedback."""
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)

        if user and user.username == username:
            # Only the logged-in user can view their own profile
            feedback = Feedback.query.filter_by(username=username).all()
            return render_template("user_profile.html", user=user, feedback=feedback)
        else:
            flash("You don't have permission to view this profile.", "error")
            return redirect("/")
    else:
        flash("You need to log in to view user profiles.", "error")
        return redirect("/login")



@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Remove the user from the database along with their feedback."""
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)

        if user and user.username == username:
            # Only the logged-in user can delete their own account
            feedback_to_delete = Feedback.query.filter_by(username=username).all()
            for feedback in feedback_to_delete:
                db.session.delete(feedback)
            db.session.delete(user)
            db.session.commit()
            session.pop("user_id")
            return redirect("/")
        else:
            flash("You don't have permission to delete this account.", "error")
            return redirect("/")
    else:
        flash("You need to log in to delete your account.", "error")
        return redirect("/login")



@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """Display a form to add feedback and add it to the user's profile."""
    form = FeedbackForm()

    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)

        if user:
            if form.validate_on_submit():
                title = form.title.data
                content = form.content.data
                feedback = Feedback(title=title, content=content, username=session["username"])  # Use session username
                db.session.add(feedback)
                db.session.commit()
                flash("Feedback added successfully!", "success")
                return redirect(url_for("user_profile", username=session["username"]))  # Use session username

            return render_template("add_feedback.html", form=form, username=username)

        else:
            flash("You need to log in to add feedback.", "error")
            return redirect("/login")
    else:
        flash("You need to log in to add feedback.", "error")
        return redirect("/login")






@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete a specific piece of feedback and redirect to /users/<username>."""
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)
        feedback = Feedback.query.get(feedback_id)

        if user and feedback:
            # Check if the logged-in user is the author of the feedback
            if user.username == feedback.username:
                db.session.delete(feedback)
                db.session.commit()
                flash("Feedback deleted successfully!", "success")
            else:
                flash("You don't have permission to delete this feedback.", "error")
        else:
            flash("Invalid feedback or user.", "error")
    else:
        flash("You need to log in to delete feedback.", "error")

    return redirect(url_for("user_profile", username=session["username"]))


@app.route("/logout")
def logout():
    """Log out user by clearing session"""
    session.pop("user_id")
    return redirect("/")