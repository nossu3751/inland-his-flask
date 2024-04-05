from flask import Blueprint, jsonify, request, abort
from app.api.v1.new_comer.services import NewComerService

new_comers_blueprint = Blueprint('new_comers', __name__, url_prefix="/api/v1/new_comers")

@new_comers_blueprint.route('/', methods=['POST'])
def upload_bulletin():
    data = request.json
    
    if not data:
        abort(400, description="Missing or invalid request data")

    try:
        _ = NewComerService.add_new_comer(data)
        return jsonify("Success"), 201
    except Exception:
        return jsonify("Failed"), 409
