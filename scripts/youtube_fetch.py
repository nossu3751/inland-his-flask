import requests

api_key = "AIzaSyB35CI_LJS0IsdgyawEWQfaua7TxjfqGvk"
channel_id = "UCuLg6_A11jThIZ2N2d0DC9A"
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
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&type=video&maxResults={max_results}&key={api_key}&order=date"
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
    if response.status_code == 200:
        return True
    return False
    
all_past_live_streams = []
while True:
    past_live_streams, next_page_token = fetch_past_live_video_list(api_key, channel_id, max_results, page_token)
    if past_live_streams:
        all_past_live_streams.extend(past_live_streams)
    if next_page_token:
        page_token = next_page_token
    else:
        break

all_videos = []
while True:
    videos, next_page_token = fetch_video_list(api_key, channel_id, max_results, page_token)
    if videos:
        all_videos.extend(videos)
    if next_page_token:
        page_token=next_page_token
    else:
        break

all_shorts = []
for video in all_videos:
    video_id = video["id"]["videoId"]
    if is_shorts(video_id):
        all_shorts.append(video)
    
