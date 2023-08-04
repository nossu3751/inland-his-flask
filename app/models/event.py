from app.extensions import db
from sqlalchemy import JSON
from sqlalchemy.sql import expression
from sqlalchemy.orm import validates
from dateutil.parser import isoparse, ParserError

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False) 
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    detail = db.Column(db.String, nullable=True)
    persons = db.Column(JSON, nullable=True)
    important = db.Column(db.Boolean, server_default=expression.false(), nullable=False)
   
    def __repr__(self):
        return f'<Event {self.title} {self.start} {self.end} {self.id}>'
    