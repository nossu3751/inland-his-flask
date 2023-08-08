from flask import Blueprint, jsonify, request
from app.api.v1.persons.services import PersonService
from app.api.v1.persons.exceptions import *
from app.api.v1.persons.utils import *
from app.api.v1.small_groups.services import SmallGroupService
import traceback


from app.utils import setup_logger

persons_blueprint = Blueprint("persons", __name__, url_prefix="/api/v1/persons")

logger = setup_logger('persons', '/var/log/inland-his-flask/persons.log')

@persons_blueprint.route("/user", methods=["GET"])
def get_person():
    user_id = request.args.get("id")
    try:
        person = PersonService.get_person(user_id)
        return jsonify({"data": person}), 200
    except PersonNotFoundException:
        logger.info(f"Person Not Found: {traceback.format_exc()}")
        return jsonify({"error": "PersonNotFound"}), 404
    except:
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify({"error":"ServerError"}), 500


@persons_blueprint.route("/", methods=["GET"])
def get_persons():
    try:
        persons = PersonService.get_persons()
        profile_images = PersonService.get_persons_profile_photos()
        return jsonify({
            "persons":persons,
            "profile_images":profile_images
        })
    except PersonNotFoundException:
        logger.info(f"Person Not Found: {traceback.format_exc()}")
        return jsonify("No persons found"), 404
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify("Unknown server error"), 500

@persons_blueprint.route("/not_admitted", methods=["GET"])
def get_not_admitted():
    try:
        not_admitted = PersonService.get_not_admitted()
        return jsonify({"data":not_admitted}), 200
    except PersonNotFoundException:
        logger.info(f"Persons Not found: {traceback.format_exc()}")
        return jsonify("No persons found"), 404
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify("Unknown server error"), 500    

@persons_blueprint.route("/admit", methods=["PUT"])
def admit_person():
    try:
        data = request.json
        person_id = data["id"]
        updated_person = PersonService.admit_person(person_id)
        return jsonify({"data": updated_person}), 201
    except Exception:
        traceback.print_exc()
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify({"error":"ServerError"}), 500
    
@persons_blueprint.route("/admit_all", methods=["PUT"])
def admit_all():
    try:
        data = request.json
        persons_id = data["id_list"]
        updated_persons = []
        for person_id in persons_id:
            updated_person = PersonService.admit_person(person_id)
            updated_persons.append(updated_person)
        return jsonify({"data":updated_persons}), 200
    except Exception:
        traceback.print_exc()
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify({"error":"ServerError"}), 500
    
@persons_blueprint.route("/add", methods=["POST"])
def add_person():
    try:
        print(request.json)
        
        birthday = request.json["birthday"]
        cell_leader = request.json["cellLeader"]
        date_of_visit = request.json["dateOfVisit"]
        email = request.json["email"]
        how_long = request.json["howLong"]
        how_visit = request.json["howVisit"]
        is_baptized = request.json["isBaptized"]
        is_searching = request.json["isSearching"]
        memo = request.json["memo"]
        name = request.json["name"]
        phone = request.json["phone"]
        who_introduced = request.json["whoIntroduced"]

        updated_user = PersonService.add_person(
            name=name,
            birthday=birthday,
            phone=phone,
            email=email,
            is_searching=is_searching,
            how_visit=how_visit,
            how_long=how_long,
            is_baptized=is_baptized,
            registered_on=date_of_visit,
            cell_leader=cell_leader,
            who_introduced=who_introduced,
            memo=memo
        )
        print(updated_user)
        member_data = SmallGroupService.person_to_member(updated_user)
        SmallGroupService.create_member(member_data)
        return jsonify(updated_user), 201
    except PersonCreateFailException:
        traceback.print_exc()
        logger.info(f"Person Create Fail: {traceback.format_exc()}")
        return jsonify("Wasn't able to add new person. "), 409
    except PersonModifyFailException:
        logger.info(f"Person Modify Fail: {traceback.format_exc()}")
        traceback.print_exc()
        return jsonify("Wasn't able to add new person. "), 409
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify("Unknown server error"), 500
        
@persons_blueprint.route("/send_verification", methods=["POST"])
def send_verification():
   
    phone_number = f'+1{request.json["phoneNumber"]}'
    name = request.json["name"]
    
    try:
        sent = PersonService.send_verification_request(phone_number, name)
        if sent:
            return jsonify({
                "message":"successfully sent verfication message"}), 201
        else:
            traceback.print_exc()
            return jsonify({"error":"ServerError"}), 500
    except PhoneNumberNotFoundException:
        logger.info(f"Phone number not found: {traceback.format_exc()}")
        return jsonify({"error":"PhoneNumberNotFound"}), 409
    except DifferentNameException:
        logger.info(f"Different name: {traceback.format_exc()}")
        return jsonify({"error":"NameMatchNotFound"}), 409
    except PersonNotAdmittedException:
        logger.info(f"Person Not Admitted: {traceback.format_exc()}")
        return jsonify({"error":"PersonNotAdmittedYet"}), 409
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        traceback.print_exc()
        return jsonify({"error":"VerificationNotSent"}), 500
    
@persons_blueprint.route("/verify", methods=["POST"])
def verify():
    phone_number = f'+1{request.json["phoneNumber"]}'
    verification_number = request.json["verificationNumber"]
    print(phone_number)
    print(verification_number)
    try:
        verified = PersonService.verify_person(phone_number, verification_number)
        if verified:
            user_session = PersonService.login(phone_number)
            token, userinfo, session_id = user_session.token, user_session.userinfo, user_session.session_id
            res = jsonify({
                "message":"User Verified",
                "data":userinfo
            })
            set_auth_cookie(res,token,userinfo,session_id)
            return res, 201
        else:
            return jsonify({"error":"WrongVerificationNumber"}), 401
    except VerificationExpiredException:
        logger.info(f"Verification Expired: {traceback.format_exc()}")
        return jsonify({"error":"VerificationExpired"}), 401
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        traceback.print_exc()
        return jsonify({"error":"ServerError"}), 500
    
@persons_blueprint.route("/authenticate", methods=["GET"])
def authenticate():
    cookies = request.cookies
    access_token_str = "inland_his_access_token"
    refresh_token_str = "inland_his_refresh_token"
    sub_str = "inland_his_sub"
    session_id_str = "inland_his_session_id"

    for s in [access_token_str, refresh_token_str, sub_str, session_id_str]:
        if s not in cookies:
            return jsonify({"error":"NotLoggedIn"}), 401
    
    access_token = cookies[access_token_str]
    refresh_token = cookies[refresh_token_str]
    sub = cookies[sub_str]
    session_id = cookies[session_id_str]

    try:
        user_session = PersonService.authenticate_person(access_token, refresh_token, sub, session_id)
        token, userinfo, session_id = user_session.token, user_session.userinfo, user_session.session_id
        if token is not None:
            res = jsonify({
                "message":"token refreshed",
                "data":userinfo,
            })
            set_auth_cookie(res, token, userinfo, session_id)
            return res, 200
        return jsonify({"data":userinfo}), 200
    except NotAuthenticatedException:
        logger.info(f"Not authenticated: {traceback.format_exc()}")
        traceback.print_exc()
        return jsonify({"error":"NotLoggedIn"}), 401
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        traceback.print_exc()
        return jsonify({"error":"ServerError"}), 500
    
@persons_blueprint.route("/logout", methods=["GET"])
def logout():
    cookies = request.cookies
    refresh_token_str = "inland_his_refresh_token"
    sub_str = "inland_his_sub"
    session_id_str = "inland_his_session_id"
    
    refresh_token = cookies[refresh_token_str]
    sub = cookies[sub_str]
    session_id = cookies[session_id_str]

    try:
        _ = PersonService.logout(refresh_token, sub, session_id)
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        traceback.print_exc()
        return jsonify({"error":"ServerError"}), 500
    finally:
        res = jsonify({"message":"UserLoggedOut"})
        remove_auth_cookie(res)
        return res, 200
    
@persons_blueprint.route('/get_profile', methods=["GET"])
def get_profile():
    cookies = request.cookies
    print(cookies)
    sub_str = "inland_his_sub"
    if sub_str not in cookies:
        return jsonify({"error":"NotLoggedIn"}), 401
    sub = cookies[sub_str]
    try:
        image_url = PersonService.get_profile_image_link_v2(sub)
        return jsonify({"data":image_url}), 200
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify({"error":"ServerError"}), 500

@persons_blueprint.route("/upload_profile/", methods=["POST"])
def upload_profile():
    logger.info("trying to upload profile")
    if 'image' not in request.files:
        logger.info("image not in request.files")
        return jsonify({"error":"NoFileFound"}), 400
    cookies = request.cookies
    print(cookies)
    sub_str = "inland_his_sub"
    
    sub = cookies[sub_str]
    logger.info("sub retrieved")
    file = request.files['image']
    if not file:
        logger.info(f"Image file is not uploaded. Can't find image file from request")
        return jsonify({"error":"NoFileFound"}), 400
    try:
        uploaded = PersonService.upload_profile_image_v2(sub, file)
        logger.info(uploaded)
        if uploaded:
            return jsonify({"message":"Success"}), 201
        else:
            return jsonify({"message":"UploadFailed"}), 500
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify({"error":"ServerError"}), 500
    
@persons_blueprint.route("/groups", methods=["GET"])
def get_groups():
    group_path = request.args.get("path")
    try:
        if group_path is None:
            groups = PersonService.get_groups()
            return jsonify({
                "data":groups,
            })
        else:
            group = PersonService.get_group_members_by_path(group_path)
            return jsonify({
                "data":group
            }), 200
    except GroupNotFoundException:
        logger.info(f"Group not found: {traceback.format_exc()}")
        return jsonify("No groups found"), 404
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        traceback.print_exc()
        return jsonify("Unknown server error"), 500
    
@persons_blueprint.route("/group/<group_id>", methods=["GET"])
def get_group(group_id):
    try:
        members = PersonService.get_group_members(group_id)
        return jsonify({
            "data":members
        }), 200
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        traceback.print_exc()
        return jsonify("Unknown server error"), 500
    

    
@persons_blueprint.route("/add_to_team", methods=["POST"])
def add_to_team():
    team_path = request.json["team_path"]
    sub = request.json["sub"]
    try:
        
        added= PersonService.add_to_team(sub, team_path)
        if added:

            return jsonify("success"), 200
        else:
            return jsonify("failed"), 409
        
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify({"error":"ServerError"}), 500

@persons_blueprint.route("/remove_from_team", methods=["POST"])
def remove_from_team():
    team_path = request.json["team_path"]
    sub = request.json["sub"]
    try:
        removed = PersonService.remove_from_team(sub, team_path)
        if removed:
            return jsonify("success"), 200
        else:
            return jsonify("failed"), 409
    except Exception:
        logger.info(f"Server Error: {traceback.format_exc()}")
        return jsonify({"error":"ServerError"}), 500


