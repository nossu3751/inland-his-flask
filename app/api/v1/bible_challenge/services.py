import datetime
import traceback
from app.models.bible_challenge import BibleChallenge
from app.models.bible import Bible
from app.extensions import db
from sqlalchemy import and_, select
from app.api.v1.bulletins.exceptions import *
from dateutil.parser import parse
from sqlalchemy import func

class BibleChallengeService:
    
    @staticmethod
    def get_all_bible_challenges():
        stmt = select(BibleChallenge).order_by(BibleChallenge.date)
        return db.session.execute(stmt).scalars()
    
    @staticmethod
    def get_bible_verses(book_name, chapter):
        stmt = select(Bible).where(and_(Bible.book_name == book_name, Bible.chapter == chapter)).order_by(Bible.verse)
        return db.session.execute(stmt).scalars()
   
    @staticmethod
    def get_bible_verses_by_challenge_date(date):
        stmt = select(BibleChallenge).where(BibleChallenge.date == date)
        result = db.session.execute(stmt).scalar_one_or_none()
        print("date", date, "result", result)
        if result:
            # Now create and execute a select statement for Bible verses matching the bookName and chapter
            verses_stmt = select(Bible).where(
                and_(
                    Bible.book_name == result.book,
                    Bible.chapter == result.chapter
                )
            ).order_by(Bible.verse)
            verses = db.session.execute(verses_stmt).scalars().all()
            # print(verses)
            return verses, result.book, result.chapter
        else:
            return None

