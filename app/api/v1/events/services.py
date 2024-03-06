from datetime import datetime
import traceback
from app.models.event import Event
from app.extensions import db
from sqlalchemy import extract, select
from sqlalchemy.exc import IntegrityError
from app.api.v1.events.exceptions import *
from app.api.v1.events.utils import split_to_multiple_start_end, get_recurring_daily, get_recurring_weekly
from app.api.v1.small_groups.services import SmallGroupService
from app.api.v1.persons.services import PersonService
from uuid import uuid4
from datetime import timedelta, datetime
from sqlalchemy import or_, cast, String

class EventService:
    @staticmethod
    def get_events():
        stmt = select(Event).order_by(Event.start.asc())
        return db.session.execute(stmt).scalars()
    
    @staticmethod
    def search_event(search_str):
        results = db.session.query(Event).filter(
            Event.title.contains(search_str),
        ).order_by(Event.start.asc()).all()
        print(results)
        return results
    
    @staticmethod
    def get_events_by_event_id(event_id):
        stmt = select(Event).where(Event.event_id == event_id).order_by(Event.start.asc())
        return db.session.execute(stmt).scalars()
    
    @staticmethod
    def get_event_start_end(event_id):
        same_events = list(EventService.get_events_by_event_id(event_id))
        if len(same_events) == 0:
            return None
        elif len(same_events) == 1:
            start = same_events[0].start.isoformat()
            end = same_events[0].end.isoformat()
        else:
            start = same_events[0].start.isoformat()
            end = same_events[-1].end.isoformat()
        return {"start":start, "end":end}
    
    @staticmethod
    def delete_events_by_event_id(event_id):
        events = EventService.get_events_by_event_id(event_id)
        try:
            for event in events:
                db.session.delete(event)
            db.session.commit()
            
        except Exception:
            traceback.print_exc()
            db.session.rollback()
            raise EventNotDeletedException("Couldn't delete event")

    
    @staticmethod
    def get_events_by_year_month(year, month):

        stmt = select(Event).where(
            extract('year', Event.start) == year,
            extract('month', Event.start) == month
        ).order_by(Event.start.asc())
        return db.session.execute(stmt).scalars()
    
    @staticmethod
    def get_event(id):
        stmt = select(Event).where(Event.id == id)
        return db.session.execute(stmt).scalar_one_or_none()
    
    @staticmethod
    def get_events_by_date(date_str):
        date = datetime.strptime(date_str, '%Y-%m-%d')
        next_day = date + timedelta(days=1)
        stmt = select(Event).filter(Event.start >= date, Event.start < next_day).order_by(Event.start)
        return db.session.execute(stmt).scalars()
    
    @staticmethod
    def edit_event(event_data:dict):
        try:
            if event_data["start"] is None or event_data["end"] is None:
                raise TimeRangeNotProvidedException("Start time or End time not provided")
            
            event_id = event_data["event_id"]
            EventService.delete_events_by_event_id(event_id)
            edited_events = EventService.add_event(event_data)
            return edited_events
        except (IntegrityError, Exception):
            traceback.print_exc()
            db.session.rollback()
            raise EventNotCreatedException("Failed to create event")
        
    @staticmethod
    def add_event(event_data:dict):
        try:
            if event_data["start"] is None or event_data["end"] is None:
                raise TimeRangeNotProvidedException("Start time or End time not provided")
            start = datetime.fromisoformat(event_data.pop("start"))
            end = datetime.fromisoformat(event_data.pop("end"))
            event_id = uuid4().hex if "event_id" not in event_data else event_data["event_id"]
            persons = event_data.pop("persons")
            repeat_option = event_data.pop("repeatOption")
            repeat_end_date = event_data.pop("repeatEndDate")
            if repeat_end_date is not None:
                repeat_end_date = datetime.fromisoformat(repeat_end_date)
            subs = {}
            if persons is not None:
                if "roles" in persons:
                    for group in persons["roles"]:
                       group_id = group["id"] 
                       group_members = PersonService.get_group_members(group_id)
                       for member in group_members:
                           subs[member["id"]] = True
                if "smallGroups" in persons:
                    for group in persons["smallGroups"]:
                        group_id = group["id"]
                        members = SmallGroupService.get_members_by_group_id(group_id)
                        for member in members:
                            if member.sub is not None:
                                subs[member.sub] = True
            persons = subs
            print("event_id", event_id)
            new_events = []
            if repeat_option is None:
                for times in split_to_multiple_start_end(start, end):
                    curr_event = event_data.copy()
                    curr_event["start"] = times["start"]
                    curr_event["end"] = times["end"]
                    curr_event["event_id"] = event_id
                    curr_event["persons"] = persons
                    new_event = Event(**curr_event)
                    print("generated event id", new_event.event_id)
                    new_events.append(new_event)
                    db.session.add(new_event)
            else:
                if int(repeat_option) == 0:
                    times_function = get_recurring_weekly
                elif int(repeat_option) == 1:
                    times_function = get_recurring_daily
                for times in times_function(start, end, repeat_end_date):
                    curr_event = event_data.copy()
                    curr_event["start"] = times["start"]
                    curr_event["end"] = times["end"]
                    curr_event["event_id"] = event_id
                    curr_event["persons"] = persons
                    new_event = Event(**curr_event)
                    print("generated event id", new_event.event_id)
                    new_events.append(new_event)
                    db.session.add(new_event)
            db.session.commit()
            return new_events
        except (IntegrityError, Exception):
            db.session.rollback()
            raise EventNotCreatedException("Failed to create event")
    

        
    