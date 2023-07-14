from flask import Blueprint, jsonify, request, abort
from app.api.v1.small_groups.services import SmallGroupService
from app.api.v1.small_groups.utils import format_small_group_data, format_small_group_data, format_member_data

small_groups_blueprint = Blueprint('small_groups', __name__, url_prefix="/api/v1/small-groups")