import os
from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db, keycloak_admin_wrapper, redis_wrapper, twilio_wrapper, s3_wrapper
from app.api.v1.videos.views import videos_blueprint
from app.api.v1.small_group_notes.views import small_group_notes_blueprint
from app.api.v1.bulletins.views import bulletins_blueprint
from app.api.v1.persons.views import persons_blueprint
from app.api.v1.small_groups.views import small_groups_blueprint
from app.api.v1.events.views import events_blueprint
from app.api.v1.polls.views import polls_blueprint
from dotenv import load_dotenv
# import logging

# def log_handler
# log_directory = '/var/logs/inland-his-flask'
# if not os.path.exists(log_directory):
#     os.makedirs(log_directory)

# logging.basicConfig()


flask_env = os.getenv("INLAND_HIS_ENV")
load_dotenv()

if flask_env == "development":
    origins = ["*"]
else:
    origins = [
        "http://localhost:4200",
        "http://www.inlandhis.com",
        "https://www.inlandhis.com",
        "http://inlandhis.com",
        "https://inlandhis.com"
    ]

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    print(origins)
    CORS(app, origins=origins, supports_credentials=True)
    
    app.config.from_object(Config)
    app.register_blueprint(videos_blueprint)
    app.register_blueprint(small_group_notes_blueprint)
    app.register_blueprint(bulletins_blueprint)
    app.register_blueprint(persons_blueprint)
    app.register_blueprint(small_groups_blueprint)
    app.register_blueprint(events_blueprint)
    app.register_blueprint(polls_blueprint)

    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

    print(TWILIO_ACCOUNT_SID)
    print(TWILIO_AUTH_TOKEN)
    print(TWILIO_PHONE_NUMBER)
    
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
    s3_wrapper.init(
        access_key=os.getenv('AWS_S3_ACCESS_KEY'),
        secret_key=os.getenv('AWS_S3_SECRET_KEY'),
        region='us-west-1',
        bucket_name=os.getenv('AWS_S3_BUCKET_NAME')
    )

    

    with app.app_context():
        db.create_all()
        
    return app