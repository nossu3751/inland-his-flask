import traceback
from flask import Blueprint, jsonify, request, abort
from app.api.v1.small_groups.services import SmallGroupService
from app.api.v1.persons.services import PersonService
from app.api.v1.small_groups.utils import format_small_group_data, format_small_groups_data, format_member_data, format_members_data, format_small_groups_data_no_members
from app.api.v1.small_groups.exceptions import *

small_groups_blueprint = Blueprint('small_groups', __name__, url_prefix="/api/v1/small-groups")


@small_groups_blueprint.route('/', methods=['GET'])
def get_small_groups():
    try:
        small_groups = SmallGroupService.get_all_small_groups()
        profile_photos = SmallGroupService.get_members_profile_photos()
        leaders = SmallGroupService.get_leaders()
        leader_sub_id_map = {leader.sub:leader.id for leader in leaders}
        leader_subs = list(leader_sub_id_map.keys())
        leaders_person_data = PersonService.get_persons_with_sub(leader_subs)
        leaders_contact = {leader_sub_id_map[leader["id"]]:leader["username"] for leader in leaders_person_data}
        return jsonify({
            "data":format_small_groups_data(small_groups),
            "profile_images": profile_photos,
            "leaders": leaders_contact
        }), 200
    except Exception:
        return jsonify({"error":"FailedToGetSmallGroups"}), 404
    
@small_groups_blueprint.route('/no_members', methods=['GET'])
def get_small_groups_no_members():
    try:
        small_groups = SmallGroupService.get_all_small_groups()
        small_groups_data = format_small_groups_data(small_groups)
        for group in small_groups_data:
            group.pop("members")
        return jsonify({
            "data": small_groups_data,
        }), 200
    except Exception:
        return jsonify({"error":"FailedToGetSmallGroups"}), 404


@small_groups_blueprint.route('/search', methods=['GET'])
def get_small_group():
    name = None
    small_group_id = None
    if "name" in request.args:
        name = request.args.get('groupName')
        small_group = SmallGroupService.get_small_group_by_name(name)
        if not small_group:
            abort(404, description=f"Small Group with Name {small_group_id} not found")
        small_group_res = format_small_group_data(small_group)
        profile_photos = SmallGroupService.get_members_profile_photos(small_group_res["members"])
        return jsonify({
            "data":small_group_res,
            "profile_images":profile_photos
        }), 200
    elif "id" in request.args:
        small_group_id = request.args.get('id')
        small_group = SmallGroupService.get_small_group_by_id(small_group_id)
        if not small_group:
            abort(404, description=f"Small Group with ID {small_group_id} not found")
        small_group_res = format_small_group_data(small_group)
        profile_photos = SmallGroupService.get_members_profile_photos(small_group_res["members"])
        return jsonify({
            "data":small_group_res,
            "profile_images":profile_photos
        }), 200
    else:
        try:
            small_groups = SmallGroupService.get_all_small_groups()
            profile_photos = SmallGroupService.get_members_profile_photos()
            return jsonify({
                "data":format_small_groups_data(small_groups),
                "profile_images": profile_photos
            }), 200
        except Exception:
            return jsonify({"error":"FailedToGetSmallGroups"}), 404
        
@small_groups_blueprint.route('/members', methods=['GET'])
def get_members():
    try:
        group_name = request.args.get('groupName')
        search_str = request.args.get('search',None)
        if search_str:
            members = SmallGroupService.search_member(search_str)
        elif not group_name:
            members = SmallGroupService.get_all_members()
        else:
            members = SmallGroupService.get_members_by_group_name(group_name)
        members = format_members_data(members)
        profile_photos = SmallGroupService.get_members_profile_photos(members)
        all_small_groups = SmallGroupService.get_all_small_groups()
        return jsonify({
            "members":members, 
            "profile_images": profile_photos,
            "small_groups": format_small_groups_data_no_members(all_small_groups)
        }), 200
    except Exception:
        return jsonify({"error":"FailedToGetSmallGroups"}), 404


@small_groups_blueprint.route('/idName', methods=['GET'])
def get_small_group_names_per_id():
    try:
        return jsonify(SmallGroupService.get_small_group_names_per_id()), 200
    except Exception:
        return jsonify({}), 404

@small_groups_blueprint.route('/create', methods=['POST'])
def create_small_group():
    data = request.json
    
    if not data:
        abort(400, description="Missing or invalid request data")
    try:
        new_small_group = SmallGroupService.create_small_group(data)
        return jsonify({"data": format_small_group_data(new_small_group)}), 201
    except DuplicateMemberException:
        return jsonify({"error":"DuplicateMembers"}), 409
    except SmallGroupNoLeaderException:
        return jsonify({"error":"NoLeader"}), 409
    except Exception:
        traceback.print_exc()
        return jsonify({"ServerError"}), 500
    
@small_groups_blueprint.route('/my_small_group',methods=['GET'])
def get_my_small_group():
    try:
        cookies = request.cookies
        print(cookies)
        sub_str = "inland_his_sub"
        if sub_str not in cookies:
            return jsonify({"error":"NotLoggedIn"}), 401
        sub = cookies[sub_str]
        print(sub)
        my_small_group = SmallGroupService.get_member_small_group(sub)
        if my_small_group is None:
            return jsonify({"error":"SmallGroupNotFound"}), 404
        my_small_group_data = format_small_group_data(my_small_group)
        profile_images = SmallGroupService.get_members_profile_photos(my_small_group_data["members"])
        leaders = SmallGroupService.get_leaders(my_small_group.id)
        leader_sub_id_map = {leader.sub:leader.id for leader in leaders}
        leader_subs = list(leader_sub_id_map.keys())
        leaders_person_data = PersonService.get_persons_with_sub(leader_subs)
        leaders_contact = {leader_sub_id_map[leader["id"]]:leader["username"] for leader in leaders_person_data}
        return jsonify({
            "data":format_small_group_data(my_small_group),
            "profile_images": profile_images,
            "leaders": leaders_contact
        }), 200
    except Exception:
        traceback.print_exc()
        return jsonify({"error":"ServerError"}), 500

@small_groups_blueprint.route('/update_group_members', methods=['PUT'])
def update_small_group_members():
    data = request.json
    if not data or "id" not in data or "members" not in data:
        abort(400, description="Missing or invalid request data")
    try:
        small_group_id = data["id"]
        SmallGroupService.update_small_group_except_members(small_group_id, data)
        members = data["members"]
        print("received member info", members)
        updated_small_group = SmallGroupService.update_small_group_members(small_group_id, members)
        return jsonify({"data":format_small_group_data(updated_small_group)})
    except SmallGroupNoLeaderException:
        return jsonify({"error":"NoLeader"}), 409
    except Exception:
        traceback.print_exc()
        return jsonify({"error":"ServerError"}), 500
# @small_groups_blueprint.route('/update', methods=['POST'])
# def create_small_group():
#     data = request.json
    
#     if not data:
#         abort(400, description="Missing or invalid request data")

#     small_group_id = data["id"]
#     updated_small_group = SmallGroupService.update_member()

#     return jsonify({"data": new_small_group}), 201