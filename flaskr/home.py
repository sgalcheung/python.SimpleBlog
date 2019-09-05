from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth.views import login_required
from flaskr import db
from flaskr.auth.models import User
from flaskr.manage.models import Blog, Comment
from flaskr.manage.views import get_comment

bp = Blueprint("home", __name__,)

@bp.route('/', methods=('GET',))
@bp.route('/index', methods=('GET',))
@bp.route('/home', methods=('GET',))
def get_all_blogs():
  """Show all the blogs, most recent first."""
  blogs = Blog.query.order_by(Blog.created_at.desc()).all()
  return render_template('index.html', blogs=blogs)

@bp.route('/blogs/<int:id>', methods=('GET','POST'))
def get_blog(id):
  """Get select blog articles and comment, also add comment."""
  if request.method == 'POST':
    content = request.form['content']
    db.session.add(Comment(blog_id=id,user_id=g.user[id],content=content))
    db.session.commit()
    return redirect(url_for('home.get_blog', id=id))

  blog = Blog.query.filter_by(id=id).first()
  comments = Comment.filter(Comment.blog_id==id).all()
  return render_template('index_blog.html', blog=blog, comments=comments)

@bp.route('/blog/<int:blog_id>/comment/<int:comment_id>/delete', methods=('POST',))
@login_required
def comment_delete(blog_id, comment_id):
  """Delete a comment.
  Ensure that the comment exists and that the logged in user is the author of the comment.
  """
  comment = get_comment(comment_id)
  db.session.delete(comment)
  db.session.commit()
  return redirect(url_for('home.get_blog', id=blog_id))
