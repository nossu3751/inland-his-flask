from datetime import datetime
from datetime import timedelta
from app.models.event import Event

def get_recurring_daily(start:datetime, end:datetime, end_repeat:datetime):
    curr_start = start
    curr_end = end
    while curr_start < end_repeat:
        yield {"start":curr_start, "end":curr_end}
        curr_start += timedelta(days=1)
        curr_end += timedelta(days=1)

def get_recurring_weekly(start:datetime, end:datetime, end_repeat:datetime):
    curr_start = start
    curr_end = end
    while curr_start < end_repeat:
        yield {"start":curr_start, "end":curr_end}
        curr_start += timedelta(weeks=1)
        curr_end += timedelta(weeks=1)
        
def get_recurring_monthly(start:datetime, end:datetime, end_repeat:datetime):
    ...

def get_prev_year_month(year:int, month: int):
    prev_year = year
    prev_month = month-1
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    return prev_year, prev_month

def get_next_year_month(year:int, month: int):
    next_year = year
    next_month = month+1
    if next_month > 12:
        next_month = 1
        next_year += 1
    return next_year, next_month

def split_to_multiple_start_end(start:datetime, end:datetime):
    curr_start = start
    curr_end = curr_start.replace(hour=23, minute=59, second=59)
    
    while curr_start < end:
        yield {"start":curr_start, "end":min(curr_end, end)}
        curr_start += timedelta(days=1)
        curr_start = curr_start.replace(hour=0, minute=0, second=0)
        curr_end = curr_start.replace(hour=23, minute=59, second=59)
def format_event_data(event:Event):
    return {
        "id": event.id,
        "event_id": event.event_id,
        "title": event.title,
        "start": event.start.isoformat(),
        "end": event.end.isoformat(),
        "detail":event.detail,
        "persons":event.persons,
        "important":event.important
    }
def format_events_data(events:list[Event]):
    return [format_event_data(event) for event in events]
  

    
