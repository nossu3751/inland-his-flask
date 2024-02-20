from flask_sqlalchemy import SQLAlchemy
from keycloak import KeycloakAdmin, KeycloakOpenID
from redis import Redis
# from twilio.rest import Client
import boto3
from botocore.config import Config

class S3Wrapper:
    def __init__(self):
        self.s3 = None
        self.bucket_name = None
    def init(self, access_key, secret_key, region, bucket_name):
        self.s3 = boto3.client(
            's3', 
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key, 
            region_name=region
        )
        self.bucket_name = bucket_name

class KeycloakAdminWrapper:
    def __init__(self):
        self.keycloak_admin = None
        self.openid = None
        self.user_password = None
        self._server_url = None
        self._admin_user_name = None
        self._admin_password = None
        self._realm_name = None
        self._client_id = None
    def init(self, server_url, username, password, realm_name, client_id, user_password):
        self.keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            username=username,
            password=password,
            realm_name=realm_name,
            client_id=client_id
        )
        # token = self.keycloak_admin.token
        # print("admin_token",token)
        self.openid = KeycloakOpenID(
            server_url=server_url,
            client_id=client_id,
            realm_name=realm_name
        )
        self.user_password = user_password
        self._server_url = server_url
        self._admin_user_name = username
        self._admin_password = password
        self._realm_name = realm_name
        self._client_id = client_id


    def relogin(self):
        self.keycloak_admin = KeycloakAdmin(
            server_url=self._server_url,
            username=self._admin_user_name,
            password=self._admin_password,
            realm_name=self._realm_name,
            client_id=self._client_id
        )

class RedisWrapper:
    def __init__(self):
        self.redis = None
    def init(self, host, port, decode_response):
        self.redis = Redis(host=host, port=port, decode_responses=decode_response)

# class TwilioWrapper:
#     def __init__(self):
#         self.twilio = None
#         self.from_phone_number = None
#     def init(self, account_sid, auth_token, from_phone):
#         print(account_sid, auth_token, from_phone)
#         self.twilio = Client(account_sid, auth_token)
#         self.from_phone_number = from_phone

keycloak_admin_wrapper =  KeycloakAdminWrapper()
redis_wrapper = RedisWrapper()
db = SQLAlchemy()
# twilio_wrapper = TwilioWrapper()
s3_wrapper = S3Wrapper()

