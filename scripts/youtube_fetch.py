import requests, os, sys
from dateutil.parser import parse
sys.path.append(f'{sys.path[0]}/..')
print(sys.path)
from app import create_app
from app.extensions import db
from app.models.video import Video

def delete_all_videos():
    Video.query.delete()
    db.session.commit()

def add_video(title, thumbnail_url, video_id, video_type, uploaded_at):
    try:
        video = Video(title=title, thumbnail_url=thumbnail_url, video_id=video_id, video_type=video_type, uploaded_at=uploaded_at)
        db.session.add(video)
        db.session.commit()
    except Exception as e:
        #Later write a log. Now just skip.
        pass


flask_env = os.getenv("INLAND_HIS_ENV")

if flask_env == "development":
    from dotenv import load_dotenv
    load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")
channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
shorts_playlist = os.getenv("YOUTUBE_SHORTS_PLAYLIST_ID")
max_results = 50
page_token = None

def fetch_past_live_video_list(api_key, channel_id, max_results=50, page_token=None):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&eventType=completed&videoType=any&order=date&maxResults={max_results}&key={api_key}"
    if page_token:
        url += f"&pageToken={page_token}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data["items"], data.get("nextPageToken")
    return None, None

def fetch_video_list(api_key, channel_id, max_results=50, page_token=None):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults={max_results}&key={api_key}&order=date"
    if page_token:
        url += f"&pageToken={page_token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["items"], data.get("nextPageToken")
    return None, None

def is_shorts(video_id):
    shorts_url = f"https://www.youtube.com/shorts/{video_id}"
    response = requests.head(shorts_url)
    print(response.headers, response.content, response.status_code)
    if response.status_code == 200:
        return True
    return False

def fetch_shorts(api_key, shorts_playlist, max_results=50, page_token=None):
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={shorts_playlist}&maxResults={max_results}&key={api_key}"
    if page_token:
        url += f"&pageToken={page_token}"
    response = requests.get(url)
    print(response.status_code, response.content)
    print("api_key:", api_key, ", playlist_id:",shorts_playlist, ", max result:", max_results, ", page token:", page_token)
    if response.status_code == 200:
        data = response.json()
        return data["items"], data.get("nextPageToken")
    return None, None

print("Retrieving live stream videos...")
all_past_live_streams = []
page_token=None
while True:
    past_live_streams, next_page_token = fetch_past_live_video_list(api_key, channel_id, max_results, page_token)
    if past_live_streams:
        all_past_live_streams.extend(past_live_streams)
    if next_page_token:
        page_token = next_page_token
    else:
        break
print(all_past_live_streams)

print("Retrieving shorts videos...")
all_shorts = []
page_token=None
while True:
    shorts, next_page_token = fetch_shorts(api_key, shorts_playlist, max_results, page_token)
    if shorts:
        all_shorts.extend(shorts)
    if next_page_token:
        page_token=next_page_token
    else:
        break
print(all_shorts)
all_shorts.sort(key=lambda x:x["snippet"]["publishedAt"], reverse=True)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        delete_all_videos()
        for live_stream in all_past_live_streams:
            video_id = live_stream["id"]["videoId"]
            title = live_stream["snippet"]["title"]
            thumbnails = live_stream["snippet"]["thumbnails"]
            if "maxres" in thumbnails:
                thumbnail_url = thumbnails["maxres"]["url"]
            elif "standard" in thumbnails:
                thumbnail_url = thumbnails["standard"]["url"]
            elif "high" in thumbnails:
                thumbnail_url = thumbnails["high"]["url"]
            elif "medium" in thumbnails:
                thumbnail_url = thumbnails["medium"]["url"]
            else:
                thumbnail_url = thumbnails["default"]["url"]  
            video_type = "live_streams"
            uploaded_at=parse(live_stream["snippet"]["publishedAt"])
            add_video(title,thumbnail_url,video_id,video_type,uploaded_at)
        for short in all_shorts:
            video_id = short["snippet"]["resourceId"]["videoId"]
            title = short["snippet"]["title"]
            thumbnails = short["snippet"]["thumbnails"]
            if "maxres" in thumbnails:
                thumbnail_url = thumbnails["maxres"]["url"]
            elif "standard" in thumbnails:
                thumbnail_url = thumbnails["standard"]["url"]
            elif "high" in thumbnails:
                thumbnail_url = thumbnails["high"]["url"]
            elif "medium" in thumbnails:
                thumbnail_url = thumbnails["medium"]["url"]
            else:
                thumbnail_url = thumbnails["default"]["url"]    
            video_type = "shorts"
            uploaded_at=parse(short["snippet"]["publishedAt"])
            add_video(title,thumbnail_url,video_id,video_type,uploaded_at)


'''
JSON Response Example

Search Results:
{
    'kind': 
    'etag': 
    'id': {
        'kind': 
        'videoId': 
    }, 
    'snippet': {
        'publishedAt': 
        'channelId': 
        'title':  
        'description': 
        'thumbnails': {
            'default': {
                'url': 
                'width': 
                'height': 
            }, 
            'medium': {
                'url': 
                'width': 
                'height': 
            }, 
            'high': {
                'url': 
                'width': 
            }
        }, 
        'channelTitle': 
        'liveBroadcastContent':
        'publishTime': 
    }
}

PlaylistFetchResults:
{
    "kind": 
    "etag": 
    "id": 
    "snippet": {
        "publishedAt": 
        "channelId": 
        "title": 
        "description": 
        "thumbnails": {
            "default": {
                "url": 
                "width": 
                "height": 
            },
            "medium": {
                "url": 
                "width": 
                "height": 
            },
            "high": {
                "url": 
                "width": 
                "height": 
            },
            "standard": {
                "url": 
                "width": 
                "height": 
            },
            "maxres": {
                "url": 
                "width": 
                "height":
            }
        },
        "channelTitle": 
        "playlistId": 
        "position":
        "resourceId": {
            "kind": 
            "videoId": 
        },
        "videoOwnerChannelTitle": 
        "videoOwnerChannelId": 
    }
}
'''
