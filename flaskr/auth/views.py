import functools
import os
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import Response

from flaskr import db
from flaskr.auth.models import User
from flaskr.utils.code import Code
from flaskr import gravatar

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
  """View decorator that redirecits anoymous users to the login page."""

  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))

    return view(**kwargs)

  return wrapped_view

@bp.before_app_request
def load_logged_in_user():
  """If a user id is stored in the session, load the user object from
  the database into ``g.user``."""
  user_id = session.get('user_id')
  g.user = User.query.get(user_id) if user_id is not None else None

@bp.route('/register', methods=('GET', 'POST'))
def register():
  """Register a new user.
  Validates that the username and email is not already taken. Hashes the password for security
  """
  if request.method == 'POST':
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    repassword = request.form["repassword"]
    error = None

    if not username:
      error = 'Username is required.'
    elif not email:
      error = 'Email is required.'
    elif not password:
      error = 'Password is required.'
    elif password != repassword:
      error = 'Passwords must match.'
    elif db.session.query(
      User.query.filter_by(username=username).exists()
    ).scalar():
      error = f"User {username} is already registered."
    elif db.session.query(
      User.query.filter_by(email=email).exists()
    ).scalar():
      error = f"User {email} is already registered."

    if error is None:
      # getting the user profile image
      link = gravatar(email, use_ssl=True)
      # the name and email is available, create the user and go to the login page
      db.session.add(User(username=username,email=email,password=password,image=link))
      db.session.commit()
      return redirect(url_for('auth.login'))

    flash(error)

  return render_template('auth/register.html')

@bp.route('/codes', methods=('GET', 'POST'))
def code():
  info = Code().create_code()
  image_file = info["image_file"]
  code = info["code"]
  session["code"] = code
  image_content = image_file.getvalue()
  print(code)
  return Response(image_content, mimetype='jpeg')

@bp.route('/login', methods=('GET', 'POST'))
def login():
  """Log in a registered user by adding the user id to the session."""
  if request.method == 'POST':
    userid = request.form['userid']
    password = request.form['password']
    vialdcode = request.form['vialdcode']
    error = None

    user = User.query.filter_by(username=userid).first() or User.query.filter_by(email=userid).first()

    if not user:
      error = 'Incorrect username or email.'
    elif not user.check_password(password):
      error = 'Incorrect password.'
    elif vialdcode != session["code"]:
      error = 'Incorrect viald code'

    if error is None:
      # store the user id in a new session and return to the index
      session.clear()
      session['user_id'] = user.id
      return redirect(url_for('manage.index'))  # jump to management home page

    flash(error)

  return render_template('auth/login.html')

@bp.route('/logout')
def logout():
  """Clear the current session, including the stored user id."""
  session.clear()
  return redirect('/')

