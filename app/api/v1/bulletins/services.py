import traceback
from app.models.bulletin import Bulletin, News, Hymn
from app.extensions import db
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload
from app.api.v1.bulletins.exceptions import *


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
    def search_bulletin(search_str):
        results = (
            db.session.query(Bulletin)
            .options(
                joinedload(Bulletin.news),
                joinedload(Bulletin.hymns)
            )
            .filter(
                or_(
                    Bulletin.sermon_title.contains(search_str),
                    Bulletin.sermon_subtitle.contains(search_str),
                    Bulletin.sermon_content.contains(search_str),
                    Bulletin.representative_prayer.contains(search_str),
                    Bulletin.community_news.contains(search_str),
                    Bulletin.message.contains(search_str),
                    Bulletin.post_message_hymn.contains(search_str),
                    Bulletin.blessing.contains(search_str),
                    News.title.contains(search_str),
                    News.description.contains(search_str),
                    Hymn.title.contains(search_str)
                )
            )
            .all()
        )
        return results
    
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
        try:
            # Step 2: Retrieve the SmallGroupNote object by its ID
            bulletin = BulletinService.get_bulletin_by_id(id)

            if bulletin is None:
                return None
            
            news = [News(**news_data) for news_data in update_data.pop("news", [])]
            hymns = [Hymn(**hymn_data) for hymn_data in update_data.pop("hymns", [])]
            bulletin.news = news
            bulletin.hymns = hymns
      
            # Step 3: Update the desired fields of the object
            for field, value in update_data.items():
                if hasattr(bulletin, field):
                    setattr(bulletin, field, value)

            db.session.commit()

            return bulletin 
        
        except Exception:
            db.session.rollback()
            raise BulletinNotModifiedException()
    
    @staticmethod
    def create_bulletin(bulletin_data):
        try:
            news = [News(**news_data) for news_data in bulletin_data.pop("news", [])]
            hymns = [Hymn(**hymn_data) for hymn_data in bulletin_data.pop("hymns", [])]
            
            new_bulletin = Bulletin(news=news, hymns=hymns, **bulletin_data)
            db.session.add(new_bulletin)
            db.session.commit()

            return new_bulletin
        except Exception:
            db.session.rollback()
            raise BulletinNotCreatedException()
        
    @staticmethod
    def delete_bulletin_by_id(bulletin_id):
        bulletin = BulletinService.get_bulletin_by_id(bulletin_id)
        try:
            db.session.delete(bulletin)
            db.session.commit()
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            raise BulletinNotDeletedException("Couldn't delete bulletin")
