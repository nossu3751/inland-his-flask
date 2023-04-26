from app.models.small_group_note import SmallGroupNote
from app.extensions import db
from .utils import parse_docx

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

