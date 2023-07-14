from flask import Blueprint, jsonify, request
from app.api.v1.persons.services import PersonService
from app.api.v1.persons.exceptions import *
from app.api.v1.persons.utils import *
import traceback

import datetime

persons_blueprint = Blueprint("persons", __name__, url_prefix="/api/v1/persons")

@persons_blueprint.route("/user", methods=["GET"])
def get_person():
    user_id = request.args.get("id")
    try:
        person = PersonService.get_person(user_id)
        return jsonify({"data": person}), 200
    except PersonNotFoundException:
        return jsonify({"error": "PersonNotFound"}), 404
    except:
        return jsonify({"error":"ServerError"}), 500


@persons_blueprint.route("/", methods=["GET"])
def get_persons():
    try:
        persons = PersonService.get_persons()
        return jsonify(persons)
    except PersonNotFoundException:
        return jsonify("No persons found"), 404
    except Exception:
        return jsonify("Unknown server error"), 500
        

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
        return jsonify(updated_user), 201
    except PersonCreateFailException:
        traceback.print_exc()
        return jsonify("Wasn't able to add new person. "), 409
    except PersonModifyFailException:
        traceback.print_exc()
        return jsonify("Wasn't able to add new person. "), 409
    except Exception:
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
        return jsonify({"error":"PhoneNumberNotFound"}), 409
    except DifferentNameException:
        return jsonify({"error":"NameMatchNotFound"}), 409
    except PersonNotAdmittedException:
        return jsonify({"error":"PersonNotAdmittedYet"}), 409
    except Exception:
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
        return jsonify({"error":"VerificationExpired"}), 401
    except Exception:
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
        return jsonify({"error":"NotLoggedIn"}), 401
    except Exception:
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
        image_url = PersonService.get_profile_image_link(sub)
        return jsonify({"data":image_url}), 200
    except Exception:
        return jsonify({"error":"ServerError"}), 500

@persons_blueprint.route("/upload_profile", methods=["POST"])
def upload_profile():
    if 'image' not in request.files:
        return jsonify({"error":"NoFileFound"}), 400
    cookies = request.cookies
    print(cookies)
    sub_str = "inland_his_sub"
    sub = cookies[sub_str]
    file = request.files['image']
    if not file:
        return jsonify({"error":"NoFileFound"}), 400
    try:
        uploaded = PersonService.upload_profile_image(sub, file)
        if uploaded:
            return jsonify({"message":"Success"}), 201
        else:
            return jsonify({"message":"UploadFailed"}), 500
    except Exception:
        return jsonify({"error":"ServerError"}), 500
    


