import traceback
from flask import Blueprint, jsonify, request, abort
from app.api.v1.app_patches.services import AppPatchService
from app.api.v1.app_patches.utils import *
from datetime import datetime, timedelta

app_patch_blueprint = Blueprint('app_patches', __name__, url_prefix="/api/v1/app_patches")
        
@app_patch_blueprint.route('/latest', methods=['GET'])
def get_app_patches():
    try:
        app_patch = AppPatchService.get_recent_app_patch()
        if app_patch:
            return jsonify(format_app_patch(app_patch))
        else:
            abort(404)
    except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": "Error occurred: {}".format(str(e))}), 500