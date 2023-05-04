from flask import abort
from app.models.small_group_note import SmallGroupNote
from app.extensions import db
from .utils import parse_docx
from sqlalchemy import select

class SmallGroupNoteService:
    @staticmethod
    def parse_and_save_docx(docx):
        parsed = parse_docx(docx)
        small_group_note = SmallGroupNote(
            html_template_data = parsed["html_template_data"],
            title = parsed["title"],
            sunday_date = parsed["sunday_date"],
            date_posted = parsed["date_posted"]
        )
        db.session.add(small_group_note)
        db.session.commit()
        return small_group_note
    
    @staticmethod
    def get_all_small_group_notes():
        stmt = select(SmallGroupNote).order_by(SmallGroupNote.date_posted.desc())
        return db.session.execute(stmt).scalars()

    @staticmethod
    def get_small_group_note_by_id(id):
        stmt = select(SmallGroupNote).where(SmallGroupNote.id == id)
        return db.session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def update_small_group_note(id, update_data):
        # Step 2: Retrieve the SmallGroupNote object by its ID
        small_group_note = SmallGroupNoteService.get_small_group_note_by_id(id)

        if small_group_note is None:
            return None

        # Step 3: Update the desired fields of the object
        if "html_template_data" in update_data:
            small_group_note.html_template_data = update_data["html_template_data"]
        if "title" in update_data:
            small_group_note.title = update_data["title"]
        if "sunday_date" in update_data:
            small_group_note.sunday_date = update_data["sunday_date"]
        if "date_posted" in update_data:
            small_group_note.date_posted = update_data["date_posted"]

        # Step 4: Commit the changes to the database
        db.session.commit()

        return small_group_note     