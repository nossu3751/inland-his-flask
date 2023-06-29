from flask import Blueprint, jsonify, request
from app.api.v1.persons.services import PersonService
import traceback
from app.api.v1.persons.exceptions import *

persons_blueprint = Blueprint("persons", __name__, url_prefix="/api/v1/persons")

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
    phone_number = request.json["phoneNumber"]
    name = request.json["name"]
    try:
        sent = PersonService.send_verification_request(phone_number, name)
        if sent:
            return jsonify({"message":"successfully sent verfication message"}), 201
        else:
            return jsonify({"error":"wasn't able to register verification number on server"}), 500
    except PhoneNumberNotFoundException:
        return jsonify({"error":"phone number not found"}), 409
    except DifferentNameException:
        return jsonify({"error":"name doesn't match"}), 409
    except PersonNotAdmittedException:
        return jsonify({"error":"this person is not admitted yet"}), 409
    except Exception:
        return jsonify({"error":"wasn't able to send verification request"}), 500
    
@persons_blueprint.route("/verify", methods=["POST"])
def verify():
    phone_number = request.json["phoneNumber"]
    verification_number = request.json["verificationNumber"]

    try:
        verified = PersonService.verify_person(phone_number, verification_number)
        if verified:
            return jsonify({"message":"successfully verified"}), 201
        else:
            return jsonify({"error":"wrong verification number"}), 401
    except VerificationExpiredException:
        return jsonify({"error":"Verification expired. Please verify again."}), 401
    except Exception:
        return jsonify({"error":"Can't verify now."}), 500
    
        
    

    

