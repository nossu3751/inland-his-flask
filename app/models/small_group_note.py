from app.extensions import db

class SmallGroupNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False)
    html_string = db.Column(db.Text, nullable=False)
    sunday_date = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f'<SmallGroupNote {self.title}>'