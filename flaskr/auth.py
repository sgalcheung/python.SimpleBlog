import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    repassword = request.form["repassword"]
    db = get_db()
    error = None

    if not username:
      error = 'Username is required.'
    elif not email:
      error = 'Email is required.'
    elif not password:
      error = 'Password is required.'
    elif password != repassword:
      error = 'Passwords must match.'
    elif db.execute(
      'SELECT id FROM users WHERE name = ?', (username,)
    ).fetchone() is not None:
      error = 'User {} is already registered.'.format(username)

    if error is None:
      db.execute(
        "INSERT INTO users (email, password, admin, name, image, created_at ) VALUES (?, ?, 0, ?, ?, datetime('now') )",
        (email, generate_password_hash(password), username,'https://cn.bing.com/images/search?view=detailV2&ccid=AJS9x%2f4s&id=55A2DBDA0ABA4CFD5DFBA0BD833178B35728EBB1&thid=OIP.AJS9x_4sHVt7DABMMJinxAHaHa&mediaurl=http%3a%2f%2fold.bz55.com%2fuploads%2fallimg%2f151207%2f140-15120F92530.jpg&exph=2048&expw=2048&q=%e5%b0%91%e5%a5%b3%e9%80%86%e5%85%89%e5%86%99%e7%9c%9f&simid=608014239721457926&selectedIndex=0')
      )
      db.commit()
      return redirect(url_for('auth.login'))

    flash(error)

  return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None

    if not username:
      error = 'Username is required.'
    elif not password:
      error = 'Password is required.'

    user = db.execute(
      'SELECT * FROM users WHERE name = ?', (username,)
    ).fetchone()

    if user is None:
      error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
      error = 'Incorrect password.'

    if error is None:
      session.clear()
      session['user_id'] = user['id']
      return redirect(url_for('blog.index'))  # jump to management blog home page

    flash(error)

  return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')

  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()

@bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('index'))

def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))

    return view(**kwargs)

  return wrapped_view