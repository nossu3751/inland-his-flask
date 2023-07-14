from app.extensions import db
from sqlalchemy import JSON
from sqlalchemy.sql import expression

class SmallGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    members = db.relationship("Member", back_populates="small_group", cascade="all, delete-orphan")
    room = db.Column(db.String, nullable=True)
    def __repr__(self):
        return f'<SmallGroup {self.name}>'
    
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sub = db.Column(db.String, nullable=True, unique=True)
    is_leader = db.Column(db.Boolean, server_default=expression.false(), nullable=False)
    small_group = db.relationship("SmallGroup", back_populates="members")
    small_group_id = db.Column(db.Integer, db.ForeignKey('small_group.id'))
    def __repr__(self):
        return f'<{"Member" if not self.is_leader else "Leader"} {self.name} {self.sub if self.sub is not None else ""}>'
    