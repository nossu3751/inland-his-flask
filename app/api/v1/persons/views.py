from flask import Blueprint, jsonify, request
from app.api.v1.persons.services import PersonService
import traceback

persons_blueprint = Blueprint("persons", __name__, url_prefix="/api/v1/persons")

@persons_blueprint.route("/", methods=["GET"])
def get_persons():
    persons = PersonService.get_persons()
    if not persons:
        return jsonify("No persons found"), 404
    return jsonify(persons)

@persons_blueprint.route("/add", methods=["POST"])
def add_person():
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

    if updated_user == None:
        traceback.print_exc()
        return jsonify("Wasn't able to add new person. "), 409
    else:
        return jsonify(updated_user), 201
