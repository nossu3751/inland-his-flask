from app.extensions import db
from sqlalchemy import JSON

class SmallGroupNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False)
    html_template_data = db.Column(JSON, nullable=False)
    sunday_date = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f'<SmallGroupNote {self.title}>'