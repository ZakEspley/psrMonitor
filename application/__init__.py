import os
from flask import Flask
from .extensions import db, oauth, login_manager, migrate
from .models import User
from .routes import main
import json
from datetime import timedelta

def create_app(test_config=None):
    # create and configure the app
    with open("client_secret.json") as jsonFile:
        clientSecrets = json.load(jsonFile)

    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite3',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='5180da4d24caad8a0de939e0c8f85707d2dc00c7f7fda5',
        GOOGLE_CLIENT_ID = clientSecrets['web']['client_id'],
        GOOGLE_CLIENT_SECRET = clientSecrets['web']['client_secret'],
        GOOGLE_DISCOVERY_URI = clientSecrets['web']['auth_uri'],
        PROFILE_SIZE = (700,700),
        MAX_IMAGE_SIZE = 1000
        # PERMANENT_SESSION_LIFETIME = timedelta(minutes=1)
    )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass
    oauth.init_app(app)
    google = oauth.register(
        name='google',
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
        client_kwargs={'scope': 'email profile'},
    )

    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(main)
    migrate.init_app(app, db)
    return app