from app.extensions import db
from app.models.video import Video
from sqlalchemy import select

class VideoService:

    @staticmethod
    def get_all_videos():
        stmt = select(Video).order_by(Video.uploaded_at.desc())
        return db.session.execute(stmt).scalars()

    @staticmethod
    def get_video_by_id(video_id):
        stmt = select(Video).where(Video.video_id == video_id)
        return db.session.execute(stmt).scalar_one_or_none()
    
    @staticmethod
    def get_all_past_live_streams():
        stmt = select(Video).where(Video.video_type == "live_streams")
        return db.session.execute(stmt).scalars()
    
    @staticmethod
    def get_live_streams_range(start, count):
        stmt = (select(Video)
                .where(Video.video_type == "live_streams")
                .order_by(Video.uploaded_at.desc())
                .offset(start)
                .limit(count))
        return db.session.execute(stmt).scalars()
    
    @staticmethod
    def get_all_shorts():
        stmt = select(Video).where(Video.video_type == "shorts")
        return db.session.execute(stmt).scalars()

