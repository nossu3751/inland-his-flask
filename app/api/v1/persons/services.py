from app.extensions import keycloak_admin_wrapper
import keycloak

class PersonService:

    @staticmethod
    def get_person(id):
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            return None
        else:
            try:
                return admin.get_user(id)
            except keycloak.exceptions.KeycloakGetError:
                return None
            
    @staticmethod
    def get_persons():
        print("hello")
        admin = keycloak_admin_wrapper.keycloak_admin
        print("admin",admin)
        if not admin:
            return None
        else:
            try:
                return admin.get_users()
            except keycloak.exceptions.KeycloakGetError:
                return None
            
    @staticmethod
    def add_person(
        name:str,
        birthday:str,
        phone:str,
        email:str,
        is_searching:str,
        how_visit:str,
        how_long:str,
        is_baptized:str,
        registered_on:str,
        cell_leader:str = "",
        who_introduced:str = "",
        memo:str = ""
    ):
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            return None
        new_comer_info = {
            "username":f"+1{phone}",
            "enabled": True,
            "email": email,
        }

        try:
            new_comer_id = admin.create_user(payload=new_comer_info)
            admin.set_user_password(new_comer_id, "password", False)

            attributes = {
                "name":[name],
                "birthday":[birthday],
                "is_searching":[is_searching],
                "how_visit":[how_visit],
                "how_long":[how_long],
                "is_baptized":[is_baptized],
                "registered_on":[registered_on],
                "cell_leader":[cell_leader],
                "who_introduced":[who_introduced],
                "memo":[memo],
                "new_comer_study_1":["not-completed"],
                "new_comer_study_2":["not-completed"],
                "new_comer_study_3":["not-completed"],
                "freshis":["not-completed"],
                "admitted":[False]

            }
            return admin.update_user(new_comer_id, {"attributes": attributes})

        except keycloak.exceptions.KeycloakPostError:
            return None
        except keycloak.exceptions.KeycloakPutError:
            admin.delete_user(new_comer_id)
            return None

    @staticmethod
    def remove_from_new_comer(id):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            admin.group_user_remove(id)
            return admin.get_user_groups(id)
        except keycloak.exceptions.KeycloakDeleteError:
            return None
        except Exception:
            return None
        
    @staticmethod
    def admit_person(id):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            attributes = admin.get_user(id).get("attributes")
            attributes["admitted"] = [True]
            admin.update_user(id, {"attributes"})
        except keycloak.exceptions.KeycloakPutError:
            return None
        except Exception:
            return None

        
        # new_comer_id = new_comer.

        