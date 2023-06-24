from flask_sqlalchemy import SQLAlchemy
from keycloak import KeycloakAdmin

class KeycloakAdminWrapper:
    def __init__(self):
        self.keycloak_admin = None
    def init(self, server_url, username, password, realm_name, client_id):
        self.keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            username=username,
            password=password,
            realm_name=realm_name,
            client_id=client_id
        )
keycloak_admin_wrapper =  KeycloakAdminWrapper()

db = SQLAlchemy()

