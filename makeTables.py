from application.extensions import db
from application import create_app
from application.models import *

db.create_all(app=create_app())