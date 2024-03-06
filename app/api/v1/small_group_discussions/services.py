import traceback
from app.models.small_group_discussion import SmallGroupDiscussion
from app.extensions import db
from sqlalchemy import select



class SmallGroupDiscussionService:
    
    
    @staticmethod
    def get_all_small_group_discussions():
        try:
            stmt = select(SmallGroupDiscussion).order_by(SmallGroupDiscussion.date.desc())
            return db.session.execute(stmt).scalars()
        except Exception:
            return None
        
    @staticmethod
    def get_recent_small_group_discussion():
        try:
            stmt = select(SmallGroupDiscussion).order_by(SmallGroupDiscussion.date.desc())
            return db.session.execute(stmt).scalars().first()
        except Exception:
            return None

    @staticmethod
    def get_small_group_discussion_by_id(id):
        stmt = select(SmallGroupDiscussion).where(SmallGroupDiscussion.id == id)
        return db.session.execute(stmt).scalar_one_or_none()
    

    @staticmethod
    def update_small_group_discussion_by_id(id, update_data):
        try:
            # Step 2: Retrieve the SmallGroupNote object by its ID
            small_group_discussion = SmallGroupDiscussionService.get_small_group_discussion_by_id(id)

            if small_group_discussion is None:
                return None

            # Step 3: Update the desired fields of the object
            for field, value in update_data.items():
                if hasattr(small_group_discussion, field):
                    setattr(small_group_discussion, field, value)

            db.session.commit()

            return small_group_discussion
        
        except Exception:
            db.session.rollback()
            raise Exception("discussion update failed")
    
    @staticmethod
    def create_small_group_discussion(data):
        try:

            new_discussion = SmallGroupDiscussion(**data)
            db.session.add(new_discussion)
            db.session.commit()

            return new_discussion
        except Exception:
            db.session.rollback()
            raise Exception("discussion create failed")
        
    @staticmethod
    def delete_small_group_discussion_by_id(id):
        bulletin = SmallGroupDiscussionService.get_small_group_discussion_by_id(id)
        try:
            db.session.delete(bulletin)
            db.session.commit()
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            raise Exception("discussion delete failed")
