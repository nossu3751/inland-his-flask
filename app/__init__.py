from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.api.v1.videos.views import *


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
