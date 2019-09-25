from flask import url_for

from flaskr import db
from flaskr.auth.models import User

class Blog(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  author_id = db.Column(db.ForeignKey(User.id), nullable=False)
  title = db.Column(db.String, nullable=False)
  summary = db.Column(db.String, nullable=False)
  content = db.Column(db.String, nullable=False)
  image = db.Column(db.String)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

  # User object backed by author_id
  # lazy="joined" means the user is returned with the user in one query
  author = db.relationship(User, lazy="joined", backref="blogs")

  @property
  def update_url(self):
    return url_for("manage.update", id=self.id)

  @property
  def delete_url(self):
    return url_for("manage.delete", id=self.id)


class Comment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  blog_id = db.Column(db.ForeignKey(Blog.id), nullable=False)
  user_id = db.Column(db.ForeignKey(User.id), nullable=False)
  content = db.Column(db.String, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

  authoruser = db.relationship(User, lazy="joined", backref="comments")
  authorblog = db.relationship(Blog, lazy="joined", backref="comments")

