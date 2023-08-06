from app.extensions import db
from sqlalchemy import JSON, func
from sqlalchemy.sql import expression
from sqlalchemy.orm import validates
from dateutil.parser import isoparse, ParserError

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False) 
    user_created = db.Column(db.String, nullable=False) 
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    detail = db.Column(db.String, nullable=True)
    options = db.Column(JSON, nullable=False) #{<option num>:<option title>}
    voted_persons = db.Column(JSON, nullable=False) #{<user sub>:<option num>}
    anonymous = db.Column(db.Boolean, server_default=expression.false(), nullable=False)
    ended = db.Column(db.Boolean, server_default=expression.false(), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    target_persons = db.Column(JSON, nullable=True) #[<user1>,<user2>,<user3>]


    def __repr__(self):
        return f'<Poll {self.title} {self.start} {self.end} {self.id}>'