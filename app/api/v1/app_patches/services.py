import traceback
from app.models.app_patch import AppPatch
from app.extensions import db
from sqlalchemy import select



class AppPatchService:
    
    @staticmethod
    def get_recent_app_patch():
        try:
            stmt = select(AppPatch).order_by(AppPatch.id.desc())
            return db.session.execute(stmt).scalars().first()
        except Exception:
            return None
       