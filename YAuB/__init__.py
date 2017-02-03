"""Logic to initialize the flask app, load the config file
register blueprints, hook up to the database, and configure flask_uploads"""

from flask import Flask
from flask_migrate import Migrate
from flask_uploads import configure_uploads
from database import db
from app import main, login_manager, uploaded_photos


def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(object_name)
    app.register_blueprint(main)
    app.debug = False
    login_manager.init_app(app)
    db.init_app(app)
    Migrate(app, db)

    configure_uploads(app, uploaded_photos)

    return app
