import traceback
from flask import Blueprint, jsonify, request, abort
from app.api.v1.polls.exceptions import *
from app.api.v1.polls.utils import *
from app.api.v1.polls.services import PollService

polls_blueprint = Blueprint("polls", __name__, url_prefix="/api/v1/polls")

@polls_blueprint.route("/", methods=["GET"])
def get_polls():
    id = request.args.get("id")
    try:
        if id:
            poll = PollService.get_poll(id)
            return jsonify({
                "data":format_poll_data(poll)
            }), 200
        else:
            polls = PollService.get_polls()
            return jsonify({
                "data":format_polls_data(polls)
            }), 200
    except Exception:
        traceback.print_exc()
        return jsonify({"error":"ServerError"}), 500
    
@polls_blueprint.route("/vote", methods=["PATCH"])
def cast_vote():
    data = request.json
    poll_id = data["id"]
    selected = data["selected"]
    cookies = request.cookies
    sub_str = "inland_his_sub"
    if sub_str not in cookies:
        return jsonify({"error":"NotLoggedIn"}), 401
    sub = cookies[sub_str]
    try:
        if id:
            poll = PollService.cast_vote(poll_id, sub, selected)
            return jsonify({
                "message":f"poll {id} selected",
                "data":poll
            }), 201
        else:
            return jsonify({
                "message":f"poll {id} doesn't exist",
                "error":"PollNotThere"
            }), 409
    except Exception:
        traceback.print_exc()
        return jsonify({"error":"ServerError"}), 500
    
@polls_blueprint.route("/end_poll", methods=["PATCH"])
def end_poll():
    id = request.args.get("id")
    cookies = request.cookies
    sub_str = "inland_his_sub"
    if sub_str not in cookies:
        return jsonify({"error":"NotLoggedIn"}), 401
    sub = cookies[sub_str]
    try:
        if id:
            poll = PollService.end_poll(id, sub)
            return jsonify({
                "message":f"poll {id} ended",
                "data":poll
            }), 201
        else:
            return jsonify({
                "message":f"poll {id} doesn't exist",
                "error":"PollNotThere"
            }), 409
    except UserNotMatchingException:
        return jsonify({
            "error":"UserNotMatching"
        }), 409
    except Exception:
        traceback.print_exc()
        return jsonify({"error":"ServerError"}), 500
    
@polls_blueprint.route("/add", methods=["POST"])
def add_poll():
    data = request.json
    cookies = request.cookies
    sub_str = "inland_his_sub"
    if sub_str not in cookies:
        return jsonify({"error":"NotLoggedIn"}), 401
    sub = cookies[sub_str]
    if not data:
        abort(400, description="Missing or invalid request data")
    try:
        poll = PollService.add_poll(data, sub)
        return jsonify({"data":format_poll_data(poll)}), 201
    except Exception:
        traceback.print_exc()
        return jsonify("ServerError"), 500