from app.models.poll import Poll

def format_poll_data(poll:Poll):
    return {
        "id": poll.id,
        "title": poll.title,
        "user_created": poll.user_created,
        "start": poll.start.isoformat(),
        "end": poll.end.isoformat(),
        "detail": poll.detail,
        "options": poll.options,
        "voted_persons": poll.voted_persons,
        "anonymous":poll.anonymous,
        "ended":poll.ended,
        "created_at":poll.created_at,
        "target_persons":poll.target_persons
    }

def format_polls_data(polls:list[Poll]):
    return [format_poll_data(poll) for poll in polls]