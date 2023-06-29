from app.extensions import keycloak_admin_wrapper, redis_wrapper, twilio_wrapper
import keycloak
import traceback
from app.api.v1.persons.exceptions import *
from random import randint


class PersonService:

    @staticmethod
    def get_person(id):
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            raise KeyCloakServerErrorException("There is a problem with Keycloak server.")
        else:
            try:
                return admin.get_user(id)
            except keycloak.exceptions.KeycloakGetError:
                raise PersonNotFoundException("User with such id is not found.")
            
    @staticmethod
    def get_persons():
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            return KeyCloakServerErrorException("There is a problem with Keycloak server.")
        else:
            try:
                return admin.get_users()
            except keycloak.exceptions.KeycloakGetError:
                raise PersonNotFoundException("Users are not found.")
            
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
        password = keycloak_admin_wrapper.user_password
        
        if not admin:
            raise KeyCloakServerErrorException("There is a problem with Keycloak server.")
        
        new_comer_info = {
            "username":f"+1{phone}",
            "enabled": True,
            "email": email,
        }

        try:
            new_comer_id = admin.create_user(payload=new_comer_info)
            admin.set_user_password(new_comer_id, password, False)
            new_comer_group_id = admin.get_group_by_path("/new-comer")["id"]
            print(new_comer_group_id)
            admin.group_user_add(new_comer_id, new_comer_group_id)

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
            raise PersonCreateFailException("Failed to create person")
        except keycloak.exceptions.KeycloakPutError:
            admin.delete_user(new_comer_id)
            raise PersonModifyFailException("Failed to add attributes")

    @staticmethod
    def remove_from_new_comer(id):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            admin.group_user_remove(id)
            return admin.get_user_groups(id)
        except keycloak.exceptions.KeycloakDeleteError:
            raise GroupRemoveFailException
        finally:
            traceback.print_exc()
        
    @staticmethod
    def admit_person(id):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            attributes = admin.get_user(id).get("attributes")
            attributes["admitted"] = [True]
            admin.update_user(id, attributes)
        except keycloak.exceptions.KeycloakPutError:
            raise AttributeModifyFailException
        except Exception:
            return None
        finally:
            traceback.print_exc()

    @staticmethod
    def authenticate_person(id):
        ...

    @staticmethod
    def login_person(id):
        ...

    @staticmethod
    def send_verification_request(phone_number, name):
        admin = keycloak_admin_wrapper.keycloak_admin

        users = admin.get_users({"username":phone_number})
        if len(users) == 0:
            raise PhoneNumberNotFoundException("Such phone number not found")
        user_id = users[0]['id']
        attributes = admin.get_user(user_id).get("attributes")
        if "admitted" not in attributes or attributes["admitted"][0] == "false":
            raise PersonNotAdmittedException("This Person is not admitted yet.")
        registered_name = attributes["name"][0] if "name" in attributes else None
        if name != registered_name:
            raise DifferentNameException("Name doesn't match")
        
        twilio = twilio_wrapper.twilio
        from_phone_number = twilio_wrapper.from_phone_number
        redis = redis_wrapper.redis
        
        if not twilio:
            raise TwilioServerErrorException("There's something wrong with Twilio server")
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        
        verification_number = randint(100000, 999999)

        try:
            _ = twilio.messages.create(
                body=f'인랜드히즈 앱 로그인 6자리 인증번호입니다: {verification_number}. (이 번호는 문자인증용 번호입니다. 답장을 받을 수 없습니다)',
                from_=from_phone_number,
                to=phone_number
            )
            return redis.set(f"{phone_number}_verification", verification_number, ex=301)
        except Exception:
            raise SendVerificationFailException("Failed to send verification request.")

    @staticmethod 
    def verify_person(phone_number, verification_number):
        redis = redis_wrapper.redis
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        else:
            correct_ver_num = redis.get(f"{phone_number}_verification")
            if correct_ver_num == None:
                raise VerificationExpiredException("Verification Expired.")
            else:
                return verification_number == correct_ver_num
            
            
    


        