from app.models.small_group_note import SmallGroupNote
from app.extensions import db
from .utils import parse_docx
from sqlalchemy import select

class SmallGroupNoteService:
    @staticmethod
    def parse_and_save_docx(docx):
        parsed = parse_docx(docx)
        small_group_note = SmallGroupNote(
            html_string = parsed["html"],
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
