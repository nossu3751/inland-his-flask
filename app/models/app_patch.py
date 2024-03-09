from app.extensions import db

class AppPatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
   
    def __repr__(self):
        return f'<AppPatch {self.id} {self.description}>'