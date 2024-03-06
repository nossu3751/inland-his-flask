import traceback
from flask import Blueprint, jsonify, request, abort
from app.api.v1.small_group_discussions.services import SmallGroupDiscussionService
from app.api.v1.small_group_discussions.utils import *
from datetime import datetime, timedelta

small_group_discussions_blueprint = Blueprint('small_group_discussions', __name__, url_prefix="/api/v1/small_group_discussions")

@small_group_discussions_blueprint.route('/', methods=['POST'])
def upload_small_group_discussion():
    try:
        data = request.json
        
        if not data:
            abort(400, description="Missing or invalid request data")
        
        new_small_group_discussion = SmallGroupDiscussionService.create_small_group_discussion(data)

        return jsonify(format_small_group_discussion(new_small_group_discussion)), 201
    except Exception:
        traceback.print_exc()
        return jsonify({
                "error": "ServerError",
        }), 500
        

@small_group_discussions_blueprint.route('/<int:id>', methods=['GET'])
def get_small_group_discussion(id):
    small_group_discussion = SmallGroupDiscussionService.get_small_group_discussion_by_id(id)

    if not small_group_discussion:
        abort(404, description=f"Small Group Discussion with ID {id} not found")

    return jsonify(format_small_group_discussion(small_group_discussion)), 200

@small_group_discussions_blueprint.route('/latest', methods=['GET'])
def get_recent_small_group_discussion():
    small_group_discussion = SmallGroupDiscussionService.get_recent_small_group_discussion()

    if not small_group_discussion:
        abort(404, description=f"Small Group Discussion not found")

    return jsonify(format_small_group_discussion(small_group_discussion)), 200


@small_group_discussions_blueprint.route('/<int:id>', methods=['DELETE'])
def delete_small_group_discussion(id):
    try:
        SmallGroupDiscussionService.delete_small_group_discussion_by_id(id)
        return jsonify(""), 200
    except Exception:
        return jsonify("ServerError"), 500

@small_group_discussions_blueprint.route('/<int:id>', methods=['PUT'])
def update_small_group_discussion(id):
    data = request.get_json()

    if not data:
        abort(400, description="Missing or invalid request data")

    updated_small_group_discussion = SmallGroupDiscussionService.update_small_group_discussion_by_id(id, data)

    if not updated_small_group_discussion:
        abort(404, description=f"Small Group Discussion with ID {id} not found")

    return jsonify(format_small_group_discussion(updated_small_group_discussion)), 200

@small_group_discussions_blueprint.route('/', methods=['GET'])
def get_small_group_discussions():
    try:
        small_group_discussions = SmallGroupDiscussionService.get_all_small_group_discussions()
        if small_group_discussions:
            return jsonify(format_small_group_discussions(small_group_discussions))
        else:
            return jsonify([]), 200
    except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": "Error occurred: {}".format(str(e))}), 500