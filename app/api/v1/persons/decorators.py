from functools import wraps
from app.extensions import keycloak_admin_wrapper
from keycloak.exceptions import KeycloakAuthenticationError
import jwt
import time, traceback

def keycloak_admin_authenticated(f):
    print("in decorator")
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("inside decorated function")
        admin = keycloak_admin_wrapper.keycloak_admin
        print(admin)
        print("admin valid in decorated function")
        def is_logged_out():
            try:
                _ = admin.get_realms()
                return False
            except KeycloakAuthenticationError:
                return True
            except Exception:
                traceback.print_exc()
                return True
        
        if admin == None or is_logged_out():
            keycloak_admin_wrapper.relogin()
        return f(*args, **kwargs)
    print("decorator function done")
    return decorated_function
    
        