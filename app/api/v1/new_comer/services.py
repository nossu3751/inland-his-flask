from datetime import datetime
import traceback
from app.api.v1.new_comer.exceptions import *
from app.models.new_comer import NewComer
from app.extensions import db
from sqlalchemy import select


class NewComerService:
    
    @staticmethod
    def add_new_comer(data):
        try:
            data['birthday'] = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
            data['registered_at'] = datetime.today().date()
            new_comer = NewComer(**data)
            db.session.add(new_comer)
            db.session.commit()
            return new_comer
        except Exception:
            db.session.rollback()
            traceback.print_exc()
            raise NewComerService()