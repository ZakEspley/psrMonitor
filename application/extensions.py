from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
migrate = Migrate()
