from app.extensions import keycloak_admin_wrapper, redis_wrapper, twilio_wrapper, s3_wrapper
import keycloak
from keycloak.exceptions import KeycloakGetError, KeycloakPostError, KeycloakAuthenticationError
import traceback, uuid, base64
from app.api.v1.persons.exceptions import *
from app.api.v1.persons.utils import dict_from_str, str_from_dict, Session, separate_moeum
from random import randint
from app.api.v1.persons.decorators import keycloak_admin_authenticated
from jamo import h2j, j2hcj
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
    def get_groups():
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
        try:
            groups = admin.get_groups()
            admin.get_group
            return [group for group in groups if "admin" not in group["name"]]
        except keycloak.exceptions.KeycloakGetError:
            raise GroupNotFoundException("Groups are not found")
        except Exception:
            raise KeyCloakServerErrorException("There is a problem with Keycloak server")

    @staticmethod
    @keycloak_admin_authenticated
    def get_group_members(group_id:str):
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
        try:
            members = admin.get_group_members(group_id)
            return members
        except Exception:
            raise KeyCloakServerErrorException("There is a problem with Keycloak server")

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
            jamo_name= "".join(separate_moeum(c) for c in j2hcj(h2j(name)))
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
                "admitted":[False],
                "hangul_name":[jamo_name]

            }
            admin.update_user(new_comer_id, {"attributes": attributes})
            return admin.get_user(new_comer_id)

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
            new_comer_group_id = admin.get_group_by_path("/new-comer")["id"]
            admin.group_user_remove(id, new_comer_group_id)
            return True
        except Exception:
            return False

    @staticmethod
    @keycloak_admin_authenticated
    def add_to_cell_leader(id):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            if not admin:
                raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
            cell_leader_group_id = admin.get_group_by_path("/cell-leader")["id"]
            admin.group_user_add(id, cell_leader_group_id)
            return True
        except Exception:
            return False
        
        
    @staticmethod
    @keycloak_admin_authenticated
    def remove_from_cell_leader(id):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            if not admin:
                raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
            cell_leader_group_id = admin.get_group_by_path("/cell-leader")["id"]
            admin.group_user_remove(id, cell_leader_group_id)
            return True
        except Exception:
            return False

    @staticmethod
    @keycloak_admin_authenticated
    def get_group_members_by_path(path:str):
        admin = keycloak_admin_wrapper.keycloak_admin
        if not admin:
            raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
        try:
            group_id = admin.get_group_by_path(path)["id"]
            members = admin.get_group_members(group_id)
            return members
        except Exception:
            raise KeyCloakServerErrorException("There is a problem with Keycloak server")
        
    @staticmethod
    @keycloak_admin_authenticated
    def add_to_team(id, team_path):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            if not admin:
                raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
            team_group_id = admin.get_group_by_path(team_path)["id"]
            admin.group_user_add(id, team_group_id)
            return True
        except Exception:
            return False
        
    @staticmethod
    @keycloak_admin_authenticated
    def remove_from_team(id, team_path):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            if not admin:
                raise  KeyCloakServerErrorException("There is a problem with Keycloak server.")
            team_group_id = admin.get_group_by_path(team_path)["id"]
            admin.group_user_remove(id, team_group_id)
            return True
        except Exception:
            return False
        
    @staticmethod
    @keycloak_admin_authenticated
    def get_not_admitted():
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            if not admin:
                return KeyCloakServerErrorException("There is a problem with Keycloak server.")
            users = PersonService.get_persons()
            not_admitted = []
            for user in users:
                print(user)
                if "attributes" not in user:
                    continue
                attributes = user.get("attributes")
                if "admitted" in attributes and attributes["admitted"][0] == "false":
                    not_admitted.append(user)
            return not_admitted
        except Exception:
            raise PersonNotFoundException("Cannot find persons")
        
    @staticmethod
    @keycloak_admin_authenticated
    def admit_person(id):
        try:
            admin = keycloak_admin_wrapper.keycloak_admin
            if not admin:
                return KeyCloakServerErrorException("There is a problem with Keycloak server.")
            attributes = admin.get_user(id).get("attributes")
            print(attributes)
            attributes["admitted"] = [True]
            
            return admin.update_user(id, {"attributes": attributes})
        
        except keycloak.exceptions.KeycloakPutError:
            traceback.print_exc()
            raise AttributeModifyFailException
        except Exception:
            traceback.print_exc()

    @staticmethod 
    def get_persons_with_sub(*subs):
        if len(subs) == 1:
            if isinstance(subs[0], list):
                subs = subs[0]
            elif isinstance(subs[0], str):
                subs = [subs[0]]
        try:
            persons = PersonService.get_persons() 
            if not subs:
                return persons
            res = [person for person in persons if person["id"] in subs]
            return res
        except Exception:
            return []
        #     person_map = {person["id"]:person for person in persons}
        #     res = [person_map[sub] for sub in subs]
        #     return res
        # except Exception:
        #     return []

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
        # print(access_token, refresh_token, sub, session_id)
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
    def get_file_name_with_profile_code(sub):
        redis = redis_wrapper.redis
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        try:
            profile_code_key = f"{sub}_profile_code"
            if redis.exists(profile_code_key):
                prev_profile_code = redis.get(profile_code_key)
                prev_file_name = f'profile_images/{sub}_{prev_profile_code}.jpg'
                return prev_file_name, profile_code_key
            else:
                return None, None
        except Exception:
            return None, None

    @staticmethod
    def upload_profile_image_v2(sub, file):
        s3 = s3_wrapper.s3
        bucket = s3_wrapper.bucket_name
        if s3 is None:
            raise S3ServerErrorException
        redis = redis_wrapper.redis
        if not redis: 
            raise RedisServerErrorException("There's something wrong with redis server")
        try:
            profile_key = f"{sub}_profile_file"
        
            if redis.exists(profile_key):
                
                prev_file_name = redis.get(profile_key)
                print("previous image existed!", prev_file_name)
                redis.delete(profile_key)
                _ = s3.delete_object(
                    Bucket=bucket,
                    Key=prev_file_name
                )

                
            code = uuid.uuid4().hex
            file_name = f'profile_images/{sub}_{code}.jpg'
            s3.upload_fileobj(
                file,
                bucket,
                file_name,
                ExtraArgs={
                    'CacheControl': 'public, max-age=31556926',
                    'ACL':'public-read'
                }
            )
            redis.set(profile_key, file_name)
            return True
            
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
    def get_profile_image_link_v2(sub):
        bucket = s3_wrapper.bucket_name
        if not bucket:
            raise S3ServerErrorException("There's something wrong with s3 server")
        redis = redis_wrapper.redis
        if not redis:
            raise RedisServerErrorException("There's something wrong with redis server")
        profile_key = f"{sub}_profile_file"
        target_image = redis.get(profile_key)
        # print("getting from redis!", target_image)
        if target_image is not None:
            image_url = f"https://{bucket}.s3.amazonaws.com/{target_image}"
            return image_url
        return None


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

    @staticmethod
    def get_persons_profile_photos(persons_data=None):
        if persons_data is None:
            persons_data = PersonService.get_persons()
        profile_image_links = {}
        try:
            for person_data in persons_data:
                sub = person_data["id"]
                try:
                    profile_image_links[sub] = PersonService.get_profile_image_link_v2(sub)
                except Exception:
                    profile_image_links[sub] = None
            return profile_image_links
        except Exception:
            return {}
        
    


            
            
    


        