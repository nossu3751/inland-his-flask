from flask_sqlalchemy import SQLAlchemy
from keycloak import KeycloakAdmin
from redis import Redis
from twilio.rest import Client
class KeycloakAdminWrapper:
    def __init__(self):
        self.keycloak_admin = None
        self.user_password = None
    def init(self, server_url, username, password, realm_name, client_id, user_password):
        self.keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            username=username,
            password=password,
            realm_name=realm_name,
            client_id=client_id
        )

class RedisWrapper:
    def __init__(self):
        self.redis = None
    def init(self, host, port, decode_response):
        self.redis = Redis(host=host, port=port, decode_responses=decode_response)

class TwilioWrapper:
    def __init__(self):
        self.twilio = None
        self.from_phone_number = None
    def init(self, account_sid, auth_token, from_phone):
        self.twilio = Client(account_sid, auth_token)
        self.from_phone_number = from_phone

keycloak_admin_wrapper =  KeycloakAdminWrapper()
redis_wrapper = RedisWrapper()
db = SQLAlchemy()
twilio_wrapper = TwilioWrapper()

