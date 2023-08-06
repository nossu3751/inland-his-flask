from datetime import datetime
import traceback
from app.models.poll import Poll
from app.api.v1.polls.exceptions import *
from app.api.v1.polls.utils import format_poll_data
from app.extensions import db
from sqlalchemy import extract, select
from sqlalchemy.exc import IntegrityError


class PollService:

    @staticmethod
    def get_polls():
        stmt = select(Poll).order_by(Poll.end.asc())
        polls = db.session.execute(stmt).scalars()
        return polls
    
    @staticmethod
    def get_poll(id):
        stmt = select(Poll).where(Poll.id == id)
        poll = db.session.execute(stmt).scalar_one_or_none()
        return poll
    
    @staticmethod
    def add_poll(poll_data, user):
        try:
            user_created = user
            if "start" not in poll_data:
                start = datetime.now()
            else:
                start = poll_data.pop("start")
                if start is None:
                    start = datetime.now()
                else:
                    start = datetime.fromisoformat(start) 
            end = datetime.fromisoformat(poll_data.pop("end"))
            ended = end <= datetime.now()
            poll_data["user_created"] = user_created
            poll_data["start"] = start
            poll_data["end"] = end
            poll_data["ended"] = ended
            poll_data["voted_persons"] = {}
            new_poll = Poll(**poll_data)
            db.session.add(new_poll)
            db.session.commit()
            return new_poll
        except (IntegrityError, Exception):
            db.session.rollback()
            raise PollNotCreatedException("Failed to create event")
        
    @staticmethod
    def end_poll(poll_id, user):
        try:
            poll = PollService.get_poll(poll_id)
            if poll:
                if poll.user_created != user:
                    raise UserNotMatchingException("Not a original poll creator")
                poll.ended = True
            db.session.commit()
            return poll_id
        except (IntegrityError, Exception):
            db.session.rollback()
            raise PollNotModifiedException("Failed to modify event")
        
    @staticmethod
    def cast_vote(poll_id, person_sub, option_id):
        try:
            poll = PollService.get_poll(poll_id)
            print("poll", poll)

            if poll:
                voted_persons = format_poll_data(poll)["voted_persons"]
                print(voted_persons)
                voted_persons[person_sub] = option_id
                print(voted_persons)
                poll.voted_persons = voted_persons
            db.session.commit()
            return poll_id
        except (IntegrityError, Exception):
            db.session.rollback()
            raise PollNotModifiedException("Failed to modify event")
        

