from app.extensions import db

class Bible(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.Integer, nullable=False)
    chapter = db.Column(db.Integer, nullable=False)
    verse = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String, nullable=True)
    book_name = db.Column(db.String, nullable=False)
   
    def __repr__(self):
        return f'<Bible {self.book_name} {self.chapter}:{self.verse}>'