from flask import Blueprint, jsonify, request
from app.api.v1.persons.services import PersonService

persons_blueprint = Blueprint("persons", __name__, url_prefix="/api/v1/persons")

@persons_blueprint.route("/", methods=["GET"])
def get_persons():
    persons = PersonService.get_persons()
    if not persons:
        return jsonify("No persons found"), 404
    return jsonify(persons)

@persons_blueprint.route("/add", methods=["POST"])
def add_person():
    birthday = request.args.get("birthday")
    cell_leader = request.args.get("cellLeader")
    date_of_visit = request.args.get("dateOfVisit")
    email = request.args.get("email")
    how_long = request.args.get("howLong")
    how_visit = request.args.get("howVisit")
    is_baptized = request.args.get("isBaptized")
    is_searching = request.args.get("isSearching")
    memo = request.args.get("memo")
    name = request.args.get("name")
    phone = request.args.get("phone")
    who_introduced = request.args.get("whoIntroduced")

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
        return jsonify("Wasn't able to add new person. "), 409
    else:
        return jsonify(updated_user), 201
