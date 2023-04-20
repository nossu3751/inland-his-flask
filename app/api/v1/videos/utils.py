def format_video_data(video):
    return {
            "title": video.title,
            "thumbnail_url": video.thumbnail_url,
            "video_id": video.video_id,
            "video_type": video.video_type,
            "uploaded_at": video.uploaded_at.isoformat()
        }

def format_videos_data(videos):
    return [format_video_data(video) for video in videos]