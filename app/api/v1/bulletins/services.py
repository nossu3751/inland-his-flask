from app.models.bulletin import Bulletin, News, Hymn
from app.extensions import db
from sqlalchemy import select


class BulletinService:
    
    
    @staticmethod
    def get_all_bulletins():
        stmt = select(Bulletin).order_by(Bulletin.sunday_date.desc())
        return db.session.execute(stmt).scalars()

    @staticmethod
    def get_bulletin_by_id(id):
        stmt = select(Bulletin).where(Bulletin.id == id)
        return db.session.execute(stmt).scalar_one_or_none()
    
    @staticmethod
    def get_bulletin_by_sunday_date(sunday_date:str):
        print(sunday_date)
        stmt = select(Bulletin).where(Bulletin.sunday_date == sunday_date)
        return db.session.execute(stmt).scalar_one_or_none()
    
    @staticmethod
    def get_bulletin_by_index(index):
        stmt = (select(Bulletin)
                .order_by(Bulletin.sunday_date.desc())
                .offset(index)
                .limit(1))
        return db.session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def update_bulletin(id, update_data):
        # Step 2: Retrieve the SmallGroupNote object by its ID
        bulletin = BulletinService.get_bulletin_by_id(id)

        if bulletin is None:
            return None

        # Step 3: Update the desired fields of the object
        for field, value in update_data.items():
            if hasattr(bulletin, field):
                setattr(bulletin, field, value)

        if "news" in update_data:
            bulletin.news = [News(**news_data) for news_data in update_data["news"]]
        if "hymns" in update_data:
            bulletin.hymns = [Hymn(**hymn_data) for hymn_data in update_data["hymns"]]

        db.session.commit()

        return bulletin 
    
    @staticmethod
    def create_bulletin(bulletin_data):
        news = [News(**news_data) for news_data in bulletin_data.pop("news", [])]
        hymns = [Hymn(**hymn_data) for hymn_data in bulletin_data.pop("hymns", [])]
        
        new_bulletin = Bulletin(news=news, hymns=hymns, **bulletin_data)
        db.session.add(new_bulletin)
        db.session.commit()

        return new_bulletin