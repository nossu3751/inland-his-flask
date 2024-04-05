from app.extensions import db

class NewComer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String, nullable=False)
    p_address = db.Column(db.String, nullable=False)
    m_address = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False)
    baptized = db.Column(db.Boolean, nullable=False)
    registered_at = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f'<NewComer {self.name}>'