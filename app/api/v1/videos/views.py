from flask import Blueprint, jsonify, request
from app.api.v1.videos.services import VideoService
from app.api.v1.videos.utils import format_videos_data

videos_blueprint = Blueprint("videos", __name__, url_prefix="/api/v1/videos")

@videos_blueprint.route("/", methods=["GET"])
def get_videos():
    videos = VideoService.get_all_videos()
    video_data = format_videos_data(videos)
    return jsonify(video_data)

@videos_blueprint.route("/shorts", methods=["GET"])
def get_shorts():
    shorts = VideoService.get_all_shorts()
    shorts_data = format_videos_data(shorts)
    return jsonify(shorts_data)

@videos_blueprint.route("/live_streams", methods=["GET"])
def get_past_live_streams():
    live_streams = VideoService.get_all_past_live_streams()
    live_stream_data = format_videos_data(live_streams)
    return jsonify(live_stream_data)

@videos_blueprint.route("/live_streams/range", methods=["GET"])
def get_live_streams_range():
    start = request.args.get('start', default = 0, type = int)
    count = request.args.get('count', default = 10, type = int)
    live_streams = VideoService.get_live_streams_range(start, count)
    live_stream_data = format_videos_data(live_streams)
    return jsonify(live_stream_data)