import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import ChangePasswordForm, UserAddForm, LoginForm, MessageForm, OnlyCsrfForm, UserEditForm
from models import db, connect_db, User, Message
from werkzeug.exceptions import Unauthorized

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

database_url = os.environ.get('DATABASE_URL', 'postgresql:///warbler')

# fix incorrect database URIs currently returned by Heroku's pg setup
database_url = database_url.replace('postgres://', 'postgresql://')

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
#toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get_or_404(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


# Reminder: logout should be POST request
@app.route('/logout')
def logout():
    """Handle logout of user."""

    # call helper function from @app.before_request
    do_logout()
    flash("You've been logged out. Have a great day!")
    
    return redirect("/login")


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    user = User.query.get_or_404(user_id)
    form = OnlyCsrfForm()
   
    return render_template('users/show.html', user=user, form=form)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f'/users/{g.user.id}/following')


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f'/users/{g.user.id}/following')

@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserEditForm(obj=g.user)
    form2 = ChangePasswordForm()

    if form.validate_on_submit():
        g.user.username = form.username.data  
        g.user.email = form.email.data   
        g.user.image_url = form.image_url.data or User.image_url.default.arg
        g.user.header_image_url = form.header_image_url.data or User.header_image_url.default.arg
        g.user.bio = form.bio.data   
        g.user.location = form.location.data  

        user = User.authenticate(form.username.data, form.password.data)

        if not user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        db.session.commit()

        id = g.user.id
        return redirect(f'/users/{id}')

    else:
        return render_template("users/edit.html", form=form, form2=form2)
    

@app.route('/users/change_password', methods=["POST"])
def change_password():
    """Change password for current user."""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form2 = ChangePasswordForm()
    
    if form2.validate_on_submit():
        g.user.current = form2.current.data
        g.user.new_password = form2.new_password.data
        g.user.confirm_password = form2.confirm_password.data
        g.user.password = g.user.change_password(g.user.current, 
                                                 g.user.new_password, 
                                                 g.user.confirm_password)
      
        db.session.commit()
        flash("Password changed successfully!")
        return redirect('/')
    else:
        return render_template("users/edit.html", form2=form2)
    
    
@app.route('/users/<int:user_id>/likes')
def user_show_likes(user_id):
    """Shows a list of user's liked messages."""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = OnlyCsrfForm()
    user = User.query.get_or_404(user_id)
    
    return render_template('users/all_likes.html', user=user, form=form)


@app.route('/users/<int:message_id>/like', methods=["POST"])
def user_like(message_id):
    """Shows a User's liked messages and handles unliking a message."""
    
    form = OnlyCsrfForm()

    if not g.user:  
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    if form.validate_on_submit():
        msg = Message.query.get_or_404(message_id)

        if msg.user_id != g.user.id:
            if msg in g.user.likes:
                g.user.likes.remove(msg) 
            
            else:
                g.user.likes.append(msg)

            db.session.commit()

            return redirect(f'/users/{g.user.id}/')
        else:
            flash("You can't like your own posts!")
            return redirect("/")
    else:
        raise Unauthorized()


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    # add csrf
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:


@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        id = g.user.id

        return redirect(f'/users/{id}')

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get_or_404(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/togglelike', methods=["POST"])
def messages_toggle_like(message_id):
    """Handles liking or unliking a message."""
   
    form = OnlyCsrfForm()
    
    if not g.user:  
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.user and form.is_submitted:
        msg = Message.query.get_or_404(message_id)
        
        if msg.user_id != g.user.id:
            if msg in g.user.likes:
                g.user.likes.remove(msg) 
    
            else:
                g.user.likes.append(msg)

            db.session.commit()

            return redirect("/")
            # consider turning liked messages into a set() for faster retrieval 
            # liked_messages = set(messages)
            # and instead of redirecting to "/" we can render home.html with liked_messages passed in
        else:
            flash("You can't like your own posts!")
            return redirect("/")
    else:
        raise Unauthorized()


@app.route('/messages/<int:message_id>/delete', methods=["GET", "POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user and request.method == 'GET':
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get_or_404(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    form = OnlyCsrfForm()

    if g.user:
        user_ids = [user.id for user in g.user.following] + [g.user.id]

        messages = (Message
                    .query
                    .order_by(Message.timestamp.desc())
                    .filter(Message.user_id.in_(user_ids))
                    .limit(100))

        return render_template('home.html', messages=messages, form=form)
    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response
