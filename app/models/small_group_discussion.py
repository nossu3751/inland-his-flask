from app.extensions import db

class SmallGroupDiscussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    html_template_data = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    
    def __repr__(self):
        return f'<SmallGroupNote {self.title}>'