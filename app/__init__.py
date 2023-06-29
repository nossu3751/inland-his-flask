import os
from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db, keycloak_admin_wrapper, redis_wrapper, twilio_wrapper
from app.api.v1.videos.views import videos_blueprint
from app.api.v1.small_group_notes.views import small_group_notes_blueprint
from app.api.v1.bulletins.views import bulletins_blueprint
from app.api.v1.persons.views import persons_blueprint

flask_env = os.getenv("INLAND_HIS_ENV")

if flask_env == "development":
    from dotenv import load_dotenv
    load_dotenv()
    origins = ["*"]
else:
    origins = [
        "http://localhost:4200/*","https://a2f8-76-90-129-219.ngrok-free.app/*","https://33d9-76-90-129-219.ngrok-free.app/*"
    ]

def create_app():
    app = Flask(__name__)
    print(origins)
    CORS(app, origins=origins)
    
    app.config.from_object(Config)
    app.register_blueprint(videos_blueprint)
    app.register_blueprint(small_group_notes_blueprint)
    app.register_blueprint(bulletins_blueprint)
    app.register_blueprint(persons_blueprint)

    db.init_app(app)
    keycloak_admin_wrapper.init(
        server_url=os.getenv('KEYCLOAK_ADMIN_SERVER_DEV') if flask_env == 'development' else os.getenv('KEYCLOAK_ADMIN_SERVER_PROD'),
        username=os.getenv('KEYCLOAK_ADMIN_USERNAME'),
        password=os.getenv('KEYCLOAK_ADMIN_PASSWORD'),
        realm_name=os.getenv('KEYCLOAK_ADMIN_REALM'),
        client_id=os.getenv('KEYCLOAK_ADMIN_CLIENT'),
        user_password=os.getenv('KEYCLOAK_DEFAULT_PASSWORD')
    )
    redis_wrapper.init(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        decode_response=True
    )
    twilio_wrapper.init(
        account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
        auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
        from_phone=os.getenv('TWILIO_PHONE_NUMBER')
    )
    

    with app.app_context():
        db.create_all()
        
    return app