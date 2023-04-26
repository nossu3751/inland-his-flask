from flask import Blueprint, jsonify, request
from app.api.v1.small_group_notes.services import SmallGroupNoteService

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
        