import traceback
from flask import Blueprint, jsonify, request, abort
from app.api.v1.events.exceptions import *
from app.api.v1.events.utils import *
from app.api.v1.events.services import EventService

events_blueprint = Blueprint("events", __name__, url_prefix="/api/v1/events")

@events_blueprint.route("/", methods=["GET"])
def get_events():
    date = request.args.get("date")
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    search = request.args.get("search")
    try:
        if search:
            events = EventService.search_event(search)
            # for i in range(100):
            #     print("from view",events)
            
        elif year and month:
            prev_year, prev_month = get_prev_year_month(year, month)
            next_year, next_month = get_next_year_month(year, month)
            prev_month_events = EventService.get_events_by_year_month(prev_year,prev_month)
            events = EventService.get_events_by_year_month(year,month)
            next_month_events = EventService.get_events_by_year_month(next_year, next_month)
            return jsonify({"data":{
                f"{prev_year}-{prev_month}": format_events_data(prev_month_events),
                f"{year}-{month}": format_events_data(events),
                f"{next_year}-{next_month}":format_events_data(next_month_events)
            }}), 200
        elif date:
            events = EventService.get_events_by_date(date)
            events = format_events_data(events)
            eids = [event["event_id"] for event in events]
            modified_start_ends = {}
            for event_id in eids:
                start_ends = EventService.get_event_start_end(event_id)
                modified_start_ends[event_id] = start_ends
            return jsonify({
                "data":events,
                "start_ends":modified_start_ends
            }), 200
        else:
            events = EventService.get_events()
        return jsonify({"data": format_events_data(events)}), 200
    except Exception:
        traceback.print_exc()
        return jsonify({"error":"ServerError"}), 500
    
@events_blueprint.route("/add", methods=["POST"])
def add_event():
    data = request.json
    print(data)
    if not data:
        abort(400, description="Missing or invalid request data")
    try:
        events = EventService.add_event(data)
        return jsonify({"data":format_events_data(events)}), 201
    except Exception:
        traceback.print_exc()
        return jsonify("ServerError"), 500
