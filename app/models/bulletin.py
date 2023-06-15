from app.extensions import db

class Bulletin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sunday_date = db.Column(db.Date, nullable=False)
    sermon_title = db.Column(db.String, nullable=False)
    sermon_subtitle = db.Column(db.String, nullable=True)
    sermon_content = db.Column(db.String, nullable=False)
    representative_prayer = db.Column(db.String, nullable=False)
    community_news = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
    post_message_hymn = db.Column(db.String, nullable=True)
    blessing = db.Column(db.String, nullable=False)
    news = db.relationship("News", back_populates="bulletin")
    hymns = db.relationship("Hymn", back_populates="bulletin")

    def __repr__(self):
        return f'<Bulletin {str(self.sunday_date)}>'

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    bulletin_id = db.Column(db.Integer, db.ForeignKey('bulletin.id'))

    bulletin = db.relationship("Bulletin", back_populates="news")

    def __repr__(self):
        return f'<News {self.title}>'

class Hymn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    bulletin_id = db.Column(db.Integer, db.ForeignKey('bulletin.id'))

    bulletin = db.relationship("Bulletin", back_populates="hymns")

    def __repr__(self):
        return f'<Hymn {self.title}>'
