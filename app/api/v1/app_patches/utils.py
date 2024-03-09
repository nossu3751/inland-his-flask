def format_app_patch(data):
    return {
        "id": data.id,
        "description": data.description,
        "date":data.date.isoformat()
    }

def format_app_patches(data):
    return [format_app_patch(d) for d in data]
