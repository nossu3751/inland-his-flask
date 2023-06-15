from flask import Blueprint, jsonify, request, abort
from app.api.v1.small_group_notes.services import SmallGroupNoteService
from app.api.v1.small_group_notes.utils import format_small_group_notes_data, format_small_group_note_data

small_group_notes_blueprint = Blueprint('small_group_notes', __name__, url_prefix="/api/v1/small-group-notes")

@small_group_notes_blueprint.route('/upload', methods=['POST'])
def upload_small_group_note():
    if 'small_group_note_file' not in request.files:
        return jsonify({"error":"No small group note file found in the request"}), 400
    
    docx = request.files['small_group_note_file']

    if docx.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if docx and docx.filename.lower().endswith('.docx'):
        small_group_note = SmallGroupNoteService.parse_and_save_docx(docx)
        return jsonify({
            "message": "File Uploaded and saved successfully",
            "small_group_note_id": small_group_note.id
        })
    return jsonify({"error": "Invalid file format"}), 400

@small_group_notes_blueprint.route("/", methods=["GET"])
def get_small_group_notes():
    small_group_notes = SmallGroupNoteService.get_all_small_group_notes()
    small_group_notes_data = format_small_group_notes_data(small_group_notes)
    return jsonify(small_group_notes_data)
        
@small_group_notes_blueprint.route('/<int:small_group_note_id>', methods=['GET'])
def get_small_group_note(small_group_note_id):
    small_group_note = SmallGroupNoteService.get_small_group_note_by_id(small_group_note_id)
    if small_group_note is None:
        abort(404, description=f"Small group note with ID {small_group_note_id} not found")

    # Assuming you have a function to convert small_group_note to a dictionary format
    small_group_note_data = format_small_group_note_data(small_group_note)
    return jsonify(small_group_note_data)


@small_group_notes_blueprint.route('/<int:small_group_note_id>', methods=['PATCH'])
def update_small_group_note(small_group_note_id):
    update_data = request.json

    if not update_data:
        return jsonify({"error": "No data provided for update"}), 400

    updated_small_group_note = SmallGroupNoteService.update_small_group_note(small_group_note_id, update_data)

    if updated_small_group_note is None:
        abort(404, description=f"Small group note with ID {small_group_note_id} not found")

    return jsonify({"message": "Small group note updated successfully", "small_group_note_id": updated_small_group_note.id})

