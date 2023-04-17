import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.api.v1.videos.views import *

flask_env = os.getenv("INLAND_HIS_ENV")

if flask_env == "development":
    from dotenv import load_dotenv
    load_dotenv()
    
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
