from app.extensions import keycloak_admin_wrapper, redis_wrapper, twilio_wrapper, s3_wrapper
import keycloak
from keycloak.exceptions import KeycloakGetError, KeycloakPostError, KeycloakAuthenticationError
import traceback, uuid, base64
from app.api.v1.persons.exceptions import *
from app.api.v1.persons.utils import dict_from_str, str_from_dict, Session
from random import randint
from app.api.v1.persons.decorators import keycloak_admin_authenticated

class PersonService:

    @staticmethod
    @keycloak_admin_authenticated
    def get_person(id=None):
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            raise KeyCloakServerErrorException("There is a problem with Keycloak server.")
        else:
            try:
                user = admin.get_user(id)
                return {
                    "attributes": user["attributes"],
                    "username": user["username"]
                }
            except keycloak.exceptions.KeycloakGetError:
                raise PersonNotFoundException("User with such id is not found.")
            
    @staticmethod
    @keycloak_admin_authenticated
    def get_persons():
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
        else:
            try:
                return admin.get_users()
            except keycloak.exceptions.KeycloakGetError:
                raise PersonNotFoundException("Users are not found.")
            
    @staticmethod
    @keycloak_admin_authenticated
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
    @keycloak_admin_authenticated
    def remove_from_new_comer(id):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            if not admin:
                raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
            admin.group_user_remove(id)
            return admin.get_user_groups(id)
        except keycloak.exceptions.KeycloakDeleteError:
            raise GroupRemoveFailException
        finally:
            traceback.print_exc()
        
    @staticmethod
    @keycloak_admin_authenticated
    def admit_person(id):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            if not admin:
                return KeyCloakServerErrorException("There is a problem with Keycloak server.")
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
    @keycloak_admin_authenticated
    def send_verification_request(phone_number, name):
     
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
        users = admin.get_users({"username":phone_number})
    
        if len(users) == 0:
            print("user")
            raise PhoneNumberNotFoundException("Such phone number not found")
        user_id = users[0]['id']
        attributes = admin.get_user(user_id).get("attributes")
        registered_name = attributes["name"][0] if "name" in attributes else None
        if name != registered_name:
            raise DifferentNameException("Name doesn't match")
        if "admitted" not in attributes or attributes["admitted"][0] == "false":
            raise PersonNotAdmittedException("This Person is not admitted yet.")
        
        
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
            return redis.set(f"{phone_number}_verification", str(verification_number), ex=301)
        except Exception:
            raise SendVerificationFailException("Failed to send verification request.")

    @staticmethod 
    def verify_person(phone_number, verification_number):

        redis = redis_wrapper.redis
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        else:
            verification_number = str(verification_number)
            key = f"{phone_number}_verification"
            correct_ver_num = redis.get(key)
            if correct_ver_num == None:
                raise VerificationExpiredException("Verification Expired.")
            else:
                verified = verification_number == correct_ver_num
                if verified:
                    redis.delete(key)
                return verified
            
    @staticmethod
    @keycloak_admin_authenticated
    def login(phone_number):
        redis = redis_wrapper.redis
        keycloak_openid = keycloak_admin_wrapper.openid
        if not keycloak_openid:
            raise KeyCloakServerErrorException("There is a problem with Keycloak server.")
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        try:
            token = keycloak_openid.token(
                username=phone_number,
                password=keycloak_admin_wrapper.user_password
            )
            userinfo = keycloak_openid.userinfo(token["access_token"])
            userinfo_str = str_from_dict(userinfo)
            session_id = uuid.uuid4().hex
            redis.set(f"{userinfo['sub']}_{session_id}", userinfo_str, ex=token["expires_in"])
            return Session(token, userinfo, session_id)
        except Exception:
            traceback.print_exc()
            
    @staticmethod
    @keycloak_admin_authenticated
    def logout(refresh_token:str, sub:str="", session_id:str=""):
        redis = redis_wrapper.redis
        keycloak_openid = keycloak_admin_wrapper.openid
        if not keycloak_openid:
            raise KeyCloakServerErrorException("There is a problem with Keycloak server.")
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        try:
            user_session = f"{sub}_{session_id}"
            if redis[user_session] is not None:
                redis.delete(user_session)
            keycloak_openid.logout(refresh_token)
            return True
        except KeycloakPostError:
            return False
        except Exception:
            return False

    @staticmethod
    def authenticate_person(access_token:str, refresh_token:str, sub:str="", session_id:str=""):
        print(access_token, refresh_token, sub, session_id)
        redis = redis_wrapper.redis
        keycloak_openid = keycloak_admin_wrapper.openid
        if not keycloak_openid:
            raise KeyCloakServerErrorException("There is a problem with Keycloak server.")
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        try:
            userinfo_str = redis.get(f"{sub}_{session_id}")
            if userinfo_str:
                userinfo = dict_from_str(userinfo_str)
                print(f"getting user from redis cache!")
                return Session(None, userinfo, session_id)
            userinfo = keycloak_openid.userinfo(access_token)
            print(f"getting user from keycloak through access token!")
            return Session(None, userinfo, session_id)
        except (KeycloakGetError, KeycloakAuthenticationError):
            try:
                token = keycloak_openid.refresh_token(refresh_token)
                userinfo = keycloak_openid.userinfo(token["access_token"])
                userinfo_str = str_from_dict(userinfo)
                redis.set(f"{sub}_{session_id}", userinfo_str, ex=token["expires_in"])
                return Session(token, userinfo, session_id)
            except KeycloakPostError:
                raise NotAuthenticatedException("Couldn't authenticate.")
        except Exception:
            traceback.print_exc()
        
    @staticmethod
    def upload_profile_image(sub, file):
        s3 = s3_wrapper.s3
        bucket = s3_wrapper.bucket_name
    
        if s3 is None:
            raise S3ServerErrorException
        redis = redis_wrapper.redis
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        try:
            profile_code_key = f"{sub}_profile_code"
            if redis.exists(profile_code_key):
                prev_profile_code = redis.get(profile_code_key)
                prev_file_name = f'profile_images/{sub}_{prev_profile_code}.jpg'
                
                _ = s3.delete_object(
                    Bucket=bucket,
                    Key=prev_file_name
                )
                
                redis.delete(profile_code_key)
                redis.delete(prev_file_name)

            code = uuid.uuid4().hex
            redis.set(profile_code_key, code)
            file_name = f'profile_images/{sub}_{code}.jpg'
            s3.upload_fileobj(
                file,
                bucket,
                file_name,
                ExtraArgs={
                    'CacheControl': 'public, max-age=31556926'
                }
            )
            
            return True
        except Exception:
            traceback.print_exc()

    @staticmethod
    def get_profile_image_link(sub):
        
        
        redis = redis_wrapper.redis
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        target_code_key = f"{sub}_profile_code"
        target_code = redis.get(target_code_key)
        target_image = f"profile_images/{sub}_{target_code}.jpg"
        image_url = redis.get(target_image)
        if image_url is not None:
            print("fetching from redis!")
            return image_url
        try:
            s3 = s3_wrapper.s3
            bucket = s3_wrapper.bucket_name
            filename = target_image
            
            image_url = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket,
                    'Key': filename
                },
                ExpiresIn=31556926)
            redis.set(target_image,image_url,ex=31556866)
            return image_url
                   
        except Exception:
            traceback.print_exc()
            raise S3ServerErrorException("Something went wrong with S3 connection")


        


            
            
    


        