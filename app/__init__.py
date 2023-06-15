import os
from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db
from app.api.v1.videos.views import videos_blueprint
from app.api.v1.small_group_notes.views import small_group_notes_blueprint
from app.api.v1.bulletins.views import bulletins_blueprint

flask_env = os.getenv("INLAND_HIS_ENV")

if flask_env == "development":
    from dotenv import load_dotenv
    load_dotenv()
    origins = "*"
else:
    origins = [
        "http://localhost:4200","https://a2f8-76-90-129-219.ngrok-free.app","https://33d9-76-90-129-219.ngrok-free.app"
    ]

def create_app():
    app = Flask(__name__)
    print(origins)
    CORS(app, origins=origins)
    
    app.config.from_object(Config)
    app.register_blueprint(videos_blueprint)
    app.register_blueprint(small_group_notes_blueprint)
    app.register_blueprint(bulletins_blueprint)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        
    return app