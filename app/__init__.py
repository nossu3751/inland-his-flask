import os
from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db
from app.api.v1.videos.views import videos_blueprint


flask_env = os.getenv("INLAND_HIS_ENV")

if flask_env == "development":
    from dotenv import load_dotenv
    load_dotenv()
    
def create_app():
    app = Flask(__name__)

    CORS(app, origins=[
        "http://localhost:4200"
    ])
    
    app.config.from_object(Config)
    app.register_blueprint(videos_blueprint)

    db.init_app(app)
    

    return app