from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint("home", __name__,)

@bp.route('/', methods=('GET',))
@bp.route('/index', methods=('GET',))
@bp.route('/home', methods=('GET',))
def get_all_blogs():
  db = get_db()
  blogs = db.execute(
    'SELECT id, user_name, user_image, title, summary, created_at'
    ' FROM blogs'
    ' ORDER BY created_at DESC'
  ).fetchall()
  return render_template('index.html', blogs=blogs)

@bp.route('/blogs/<int:id>')
def get_blog(id):
  blog = get_db().execute(
    'SELECT user_name, user_image, title, content, created_at'
    ' FROM blogs'
    ' WHERE id = ?',
    (id,)
  ).fetchone()
  return render_template('index_blog.html', blog=blog)
