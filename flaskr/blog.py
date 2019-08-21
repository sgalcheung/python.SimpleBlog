from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__, url_prefix='/blog')


@bp.route('/index', methods=('GET', 'POST'))
def index():
  db = get_db()
  blogs = db.execute(
    'SELECT b.id, title, summary, b.created_at, user_id, name'
    ' FROM blogs b JOIN users u ON b.user_id = u.id'
    ' ORDER BY b.created_at DESC'
  ).fetchall()
  return render_template("blog/index.html", blogs=blogs)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
  if request.method == 'POST':
    title = request.form['title']
    summary = request.form['summary']
    content = request.form['content']
    error = None

    if not title:
      error = 'Title is required.'

    if error is not None:
      flash(error)
    else:
      db = get_db()
      db.execute(
        'INSERT INTO blogs (user_id, user_name, user_image, title, summary, content, created_at)'
        " VALUES (?, ?, 'https://cn.bing.com', ?, ?, ?, datetime('now'))",
        (g.user['id'], g.user['name'], title, summary, content)
      )
      db.commit()
      return redirect(url_for('blog.index'))

  return render_template('blog/create.html')

def get_blog(id, check_author=True):
  blog = get_db().execute(
    'SELECT b.id, title, summary, content, created_at, user_id, name'
    ' FROM blogs b JOIN users u ON b.user_id = u.id'
    ' WHERE b.id = ?',
    (id,)
  ).fetchone()

  if blog is None:
    abort(404, "Blog id {0} doesn't exist.".format(id))

  if check_author and blog['user_id'] != g.user['id']:
    abort(403)

  return blog

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
  blog = get_blog(id)

  if request.method == 'POST':
    title = request.form['title']
    summary = request.form['summary']
    content = request.form['content']
    error = None

    if not title:
      errror = 'Title is required.'

    if error is not None:
      flash(error)
    else:
      db = get_db()
      db.execute(
        'UPDATE blogs SET title = ?, summary = ?, content = ?'
        ' WHERE id = ?',
        (title, summary, content)
      )
      db.commit()
      return redirect(url_for('blog.index'))

  return render_template('blog/update.html', blog=blog)

def delete(id):
  get_blog(id)
  db = get_db()
  db.execute('DELETE FROM blogs WHERE id = ?', (id,))
  db.commit()
  return redirect(url_for('blog.index'))