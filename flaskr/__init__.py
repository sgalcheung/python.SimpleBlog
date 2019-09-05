import os

import click
from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
  """Create and configure an instance of the Flask application."""
  app = Flask(__name__, instance_relative_config=True)

  # some deploy system set the database url in the environ
  db_url = os.environ.get("DATABASE_URL")

  if db_url is None:
    # default to a sqlite database in the instance folder
    db_url = "sqlite:///" + os.path.join(app.instance_path, "flaskr.sqlite")
    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

  app.config.from_mapping(
    # default secret that should be overridden in environ or config
    SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
    SQLALCHEMY_DATABASE_URI=db_url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
  )

  if test_config is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile("config.py", silent=True)
  else:
    # load the test config if passed in
    app.config.update(test_config)

  # initialized Flask-SQLAlchemy and the init-db command
  db.init_app(app)
  app.cli.add_command(init_db_command)

  # a simple page that says hello
  @app.route('/hello/')
  def hello():
    return 'Hello, World!'

  # Returns a dictionary with a context processor,
  # and the key in the dictionary is rendered as a variable in the template.
  import time

  @app.context_processor
  def get_current_time():
    def get_time(timeFormat="%Y-%m-%d %H:%M:%S"):
      return time.strftime(timeFormat)
    return dict(current_time=get_time)

  # apply the blueprints to the app
  from flaskr import auth, manage, home

  app.register_blueprint(auth.bp)
  app.register_blueprint(manage.bp)
  app.register_blueprint(home.bp)

  # make "index" point at "/", which is handled by "blog.index"
  # app.add_url_rule("/", endpoint="index")

  return app


def init_db():
  db.drop_all()
  db.create_all()

@click.command("init-db")
@with_appcontext
def init_db_command():
  """Clear existing data and craete new tables."""
  init_db()
  click.echo("Initialized the database.")