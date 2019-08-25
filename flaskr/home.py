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

@bp.route('/blogs/<int:id>', methods=('GET','POST'))
def get_blog(id):
  if request.method == 'POST':
    content = request.form['content']
    db = get_db()
    db.execute(
      'INSERT INTO comments (blog_id, user_id, user_name, user_image, content, created_at)'
      "VALUES (?, ?, ?, ?, ?, datetime('now'))",
      (id, g.user['id'], g.user['name'], g.user['image'], content)
    )
    db.commit()
    return redirect(url_for('home.get_blog', id=id))

  blog = get_db().execute(
    'SELECT id, user_id, user_name, user_image, title, content, created_at'
    ' FROM blogs'
    ' WHERE id = ?',
    (id,)
  ).fetchone()
  comments = get_db().execute(
    'SELECT id, blog_id, user_id, user_name, user_image, content, created_at'
    ' FROM comments'
    ' WHERE blog_id = ?'
    ' ORDER BY created_at DESC',
    (id,)
  ).fetchall()
  return render_template('index_blog.html', blog=blog, comments=comments)

@bp.route('/blog/<int:blog_id>/comment/<int:comment_id>/delete', methods=('POST',))
@login_required
def comment_delete(blog_id, comment_id):
  # Verify existence
  db = get_db()
  comment = db.execute(
    'SELECT c.id, content, c.created_at, user_id, name'
    ' FROM comments c JOIN users u ON c.user_id = u.id'
    ' WHERE c.id = ?',
    (comment_id,)
  ).fetchone()

  if comment is None:
    abort(404, "Comment id {0} doesn't exist.".format(comment_id))

  db.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
  db.commit()
  return redirect(url_for('home.get_blog', id=blog_id))
