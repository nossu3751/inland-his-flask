def format_small_group_discussion(data):
    return {
        "id": data.id,
        "html_template_data": data.html_template_data,
        "date":data.date.isoformat()
    }

def format_small_group_discussions(data):
    return [format_small_group_discussion(d) for d in data]
