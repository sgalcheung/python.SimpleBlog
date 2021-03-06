from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr import db
from flaskr.auth.views import login_required
from flaskr.manage.models import Blog, Comment
from flaskr.auth.models import User
import os
from flask import send_from_directory

bp = Blueprint("manage", __name__, url_prefix='/manage')
UPLOAD_FOLDER_BLOG = 'flaskr/static/img/blog'

@bp.route('/')
def index():
  """Redirect "/" to "/blogs", because other place use url_for(manage.index)"""
  return redirect(url_for('manage.manage_blogs'))


@bp.route('/blogs', methods=('GET',))
@login_required
def manage_blogs():
  """Show all the blogs, most recent first."""
  blogs = Blog.query.order_by(Blog.created_at.desc()).all()
  return render_template('manage/manage_blogs.html', blogs=blogs)


def get_blog(id, check_author=True):
  """Get a blog and its author by id.
  Checks that the id exists and optionally that the current user is the author
  :param id: id of blog to get
  :param check_author: required the current user to the author
  :return: the blog with author information
  :raise 404: if a blog with the given id doesn't exists
  :raise 403: if the current user isn't the author
  """
  blog = Blog.query.get_or_404(id, f"Blog id {id} doesn't exists.")

  if check_author and blog.author != g.user:
    abort(403)

  return blog

def allowed_file(filename):
  ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/blog/create', methods=('GET', 'POST'))
@login_required
def blog_create():
  if request.method == 'POST':
    error = None
    mark_left = '<'
    mark_right = '/>'
    title = request.form['title']
    summary = request.form['summary']
    content = request.form['content']
    if (mark_left in title or mark_right in title) or \
       (mark_left in summary or mark_right in summary) or \
       (mark_left in content or mark_right in content):
      error = "Input containing '<' or '/>' is not allowed."

    file = request.files['file']
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      # ensure the folder exists
      os.makedirs(UPLOAD_FOLDER_BLOG, exist_ok=True)
      file.save(os.path.join(UPLOAD_FOLDER_BLOG, filename))


    if not title:
      error = 'Title is required.'

    if error is not None:
      flash(error)
    else:
      db.session.add(Blog(title=title, summary=summary, content=content, author=g.user, image=file.filename))
      db.session.commit()
      return redirect(url_for('manage.index'))

  return render_template('manage/blog_create.html')


@bp.route('/blog/<int:id>/update', methods=('GET', 'POST'))
@login_required
def blog_update(id):
  """Update a blog if the current user id the author,
  because I have opened up the administrator's authority to operate ordinary users,
  so admin can update too and  "check_author=Flase".
  """
  blog = get_blog(id, False)

  if request.method == 'POST':
    error = None
    mark_left = '<'
    mark_right = '/>'
    title = request.form['title']
    summary = request.form['summary']
    content = request.form['content']
    if (mark_left in title or mark_right in title) or \
       (mark_left in summary or mark_right in summary) or \
       (mark_left in content or mark_right in content):
      error = "Input containing '<' or '/>' is not allowed."

    file = request.files['file']
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file_url = 'img/blog/' + filename
      # ensure the folder exists
      os.makedirs(UPLOAD_FOLDER_BLOG, exist_ok=True)
      file.save(os.path.join(UPLOAD_FOLDER_BLOG, filename))

    if not title:
      errror = 'Title is required.'

    if error is not None:
      flash(error)
    else:
      blog.title = title
      blog.summary = summary
      blog.content = content
      blog.image = file_url
      db.session.commit()
      return redirect(url_for('manage.index'))

  return render_template('manage/blog_update.html', blog=blog)


@bp.route('/blog/<int:id>/delete', methods=('POST',))
@login_required
def blog_delete(id):
  """Delete a blog.
  Ensure that the blog exists and that the logged in user is the author of the blog.
  because I have opened up the administrator's authority to operate ordinary users,
  so admin can delete too and  "check_author=Flase".
  """
  blog = get_blog(id, False)
  comments = Comment.query.filter(Comment.blog_id==blog.id).all()
  [db.session.delete(comment) for comment in comments]
  db.session.delete(blog)
  db.session.commit()
  return redirect(url_for('manage.index'))


def get_comment(id, check_author=True):
  """Get a comment and its author by id.
  Checks that the id exists and optionally that the current user is the author
  :param id: id of comment to get
  :param check_author: required the current user to the author
  :return: the comment with author information
  :raise 404: if a comment with the given id doesn't exists
  :raise 403: if the current user isn't the author
  """
  comment = Comment.query.get_or_404(id, f"Comment id {id} doesn't exists.")

  if check_author and comment.authoruser != g.user:
    abort(403)

  return comment


@bp.route('/comments', methods=('GET',))
@login_required
def manage_comments():
  """Show all the comments, most recent first."""
  comments = Comment.query.order_by(Comment.created_at.desc()).all()
  return render_template('manage/manage_comments.html', comments=comments)


@bp.route('/comment/<int:id>/delete', methods=('POST',))
@login_required
def comment_delete(id):
  """Delete a comment.
  Ensure that the comment exists and that the logged in user is the
  author of the comment.
  """
  comment = get_comment(id)
  db.session.delete(comment)
  db.session.commit()
  return redirect(url_for('manage.manage_comments'))


@bp.route('/users', methods=('GET',))
@login_required
def manage_users():
  """Show all the users, most recent first."""
  users = User.query.order_by(User.created_at.desc()).all()
  return render_template('manage/manage_users.html', users=users)


def get_user(id):
  """Get a user and its author by id.
  :param id: id of user to get
  :return: the user with author information
  :raise 404: if a user with the given id doesn't exists
  """
  user = User.query.get_or_404(id, f"User id {id} doesn't exists.")

  return user


@bp.route('/user/<int:id>/delete', methods=('POST',))
def user_delete(id):
  """Delete a user.
  Ensure that the user exists
  """
  user = get_user(id)
  blogs = Blog.query.filter(Blog.author_id==user.id).all()
  # delete comment=>blog=>user
  for blog in blogs:
    comments = Comment.query.filter(Comment.blog_id==blog.id).all()
    [db.session.delete(comment) for comment in comments]
  [db.session.delete(blog) for blog in blogs]
  db.session.delete(user)
  db.session.commit()
  return redirect(url_for('manage.manage_users'))
