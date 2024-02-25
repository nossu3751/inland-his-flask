from app.extensions import db

class BibleChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String, nullable=True)
    book = db.Column(db.String, nullable=True)
    chapter = db.Column(db.Integer, nullable=True)
   
    def __repr__(self):
        return f'<BibleChallenge {self.title}>'