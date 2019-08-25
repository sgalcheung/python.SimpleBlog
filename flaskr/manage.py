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

bp = Blueprint("manage", __name__, url_prefix='/manage')

@bp.route('/')
def index():
  return redirect(url_for('manage.manage_blogs'))

@bp.route('/blogs', methods=('GET',))
def manage_blogs():
  db = get_db()
  blogs = db.execute(
    'SELECT b.id, title, summary, b.created_at, user_id, name'
    ' FROM blogs b JOIN users u ON b.user_id = u.id'
    ' ORDER BY b.created_at DESC'
  ).fetchall()
  return render_template('manage/manage_blogs.html', blogs=blogs)

@bp.route('/blog/create', methods=('GET', 'POST'))
@login_required
def blog_create():
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
        " VALUES (?, ?, 'img/gettyvilla.jpg', ?, ?, ?, datetime('now'))",
        (g.user['id'], g.user['name'], title, summary, content)
      )
      db.commit()
      return redirect(url_for('manage.index'))

  return render_template('manage/blog_create.html')

def get_blog(id, check_author=True):
  blog = get_db().execute(
    'SELECT b.id, title, summary, content, b.created_at, user_id, name'
    ' FROM blogs b JOIN users u ON b.user_id = u.id'
    ' WHERE b.id = ?',
    (id,)
  ).fetchone()

  if blog is None:
    abort(404, "Blog id {0} doesn't exist.".format(id))

  if check_author and blog['user_id'] != g.user['id']:
    abort(403)

  return blog

@bp.route('/blog/<int:id>/update', methods=('GET', 'POST'))
@login_required
def blog_update(id):
  blog = get_blog(id, False)  # Because I have opened up the administrator's authority to operate ordinary users.

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
        "UPDATE blogs SET title = ?, summary = ?, content = ?, created_at = datetime('now')"
        ' WHERE id = ?',
        (title, summary, content, id)
      )
      db.commit()
      return redirect(url_for('manage.index'))

  return render_template('manage/blog_update.html', blog=blog)

@bp.route('/blog/<int:id>/delete', methods=('POST',))
@login_required
def blog_delete(id):
  get_blog(id, False)
  db = get_db()
  db.execute('DELETE FROM blogs WHERE id = ?', (id,))
  db.commit()
  return redirect(url_for('manage.index'))

@bp.route('/comments', methods=('GET',))
@login_required
def manage_comments():
  db = get_db()
  comments=db.execute(
    'SELECT c.id, blog_id, user_id, user_name, user_image, content, c.created_at'
    ' FROM comments c JOIN users u ON c.user_id = u.id'
    ' ORDER BY c.created_at DESC'
  ).fetchall()
  return render_template('manage/manage_comments.html', comments=comments)

@bp.route('/comment/<int:id>/delete', methods=('POST',))
@login_required
def comment_delete(id):
  # Verify existence
  db = get_db()
  comment = db.execute(
    'SELECT c.id, content, c.created_at, user_id, name'
    ' FROM comments c JOIN users u ON c.user_id = u.id'
    ' WHERE c.id = ?',
    (id,)
  ).fetchone()

  if comment is None:
    abort(404, "Comment id {0} doesn't exist.".format(id))

  db.execute('DELETE FROM comments WHERE id = ?', (id,))
  db.commit()
  return redirect(url_for('manage.manage_comments'))

@bp.route('/users', methods=('GET',))
@login_required
def manage_users():
  db = get_db()
  users = db.execute(
    'SELECT id, email, password, admin, name, image, created_at'
    ' FROM users'
    ' ORDER BY created_at DESC'
  ).fetchall()
  return render_template('manage/manage_users.html', users=users)

@bp.route('/user/<int:id>/delete', methods=('POST',))
def user_delete(id):
  # Verify existence
  db = get_db()
  user = db.execute(
    'SELECT id, email, password, admin, name, image, created_at'
    ' FROM users'
    ' WHERE id = ?',
    (id,)
  ).fetchone()

  if user is None:
    abort(404, "User id {0} doesn't exist.".format(id))

  # delete relevant comments, blogs, finally delete this user
  db.execute(
    'DELETE FROM comments WHERE user_id = ?'
    ,(id,)
  )
  db.execute(
    'DELETE FROM blogs WHERE user_id = ?'
    ,(id,)
  )
  db.execute(
    'DELETE FROM users WHERE id = ?'
    ,(id,)
  )
  db.commit()
  return redirect(url_for('manage.manage_users'))
