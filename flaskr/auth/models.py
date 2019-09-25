from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flaskr import db


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String, unique=True, nullable=False)
  username = db.Column(db.String, unique=True, nullable=False)
  _password = db.Column("password", db.String, nullable=False)
  admin = db.Column(db.Boolean, nullable=False, default=False)
  image = db.Column(db.String, nullable=False, default="http://www.gravatar.com/avatar/c788172c2ba2da1eee150b7afb1fe983?d=mm&s=120")
  created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())

  @hybrid_property
  def password(self):
    return self._password

  @password.setter
  def password(self, value):
    """Store the password as a hash for security."""
    self._password = generate_password_hash(value)

  def check_password(self, value):
    return check_password_hash(self.password, value)
