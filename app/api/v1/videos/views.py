from flask import Blueprint, jsonify, request
from app.api.v1.videos.services import VideoService
from app.api.v1.videos.utils import format_videos_data, format_video_data

videos_blueprint = Blueprint("videos", __name__, url_prefix="/api/v1/videos")

@videos_blueprint.route("/", methods=["GET"])
def get_videos():
    try:
        videos = VideoService.get_all_videos()
        video_data = format_videos_data(videos)
        return jsonify(video_data)
    except Exception:
        return jsonify({"error":"ServerError"}), 500

@videos_blueprint.route("/shorts", methods=["GET"])
def get_shorts():
    shorts = VideoService.get_all_shorts()
    shorts_data = format_videos_data(shorts)
    return jsonify(shorts_data)

@videos_blueprint.route("/live_streams", methods=["GET"])
def get_live_streams():
    video_id = request.args.get('id')
    index = request.args.get('index')
    search_str = request.args.get('search',None)
    print(search_str)
    try:
        if search_str:
            live_streams = VideoService.search_live_streams(search_str)
            return jsonify({"data":format_videos_data(live_streams)}), 200
        elif video_id is not None:
            live_stream = VideoService.get_video_by_id(video_id)
            if live_stream is not None:
                live_stream_data = format_video_data(live_stream)  
                return jsonify(live_stream_data)
            else:
                return jsonify({"error": "No video with that id found"}), 404
        elif index is not None:
            live_stream = VideoService.get_live_streams_by_index(index)
            if live_stream is not None:
                live_stream_data = format_video_data(live_stream)  
                return jsonify(live_stream_data)
            else:
                return jsonify({"error": "No video at index"}), 404
        else:
            live_streams = VideoService.get_all_past_live_streams()
            if live_streams is not None:
                live_stream_data = format_videos_data(live_streams)
                return jsonify(live_stream_data)
            else:
                return jsonify({"error": "No videos found", "data":[]}), 200
    except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({"error": "Error occurred: {}".format(str(e))}), 500
# def get_past_live_streams():
#     live_streams = VideoService.get_all_past_live_streams()
#     live_stream_data = format_videos_data(live_streams)
#     return jsonify(live_stream_data)

@videos_blueprint.route("/live_streams/<int:index>", methods=["GET"])
def get_live_stream_by_index(index):
    try:
        live_stream = VideoService.get_live_streams_by_index(index)
        if live_stream is not None:
            live_stream_data = format_video_data(live_stream)  
            return jsonify(live_stream_data)
        else:
            return jsonify({"error": "No video at index"}), 404
    except Exception as e:
        return jsonify({"error": "Error occurred: {}".format(str(e))}), 500
    
# @videos_blueprint.route("/live_streams/<int:index>", methods=["GET"])
# def get_live_stream_by_id(video_id):
#     try:
#         live_stream = VideoService.get_video_by_id(video_id)
#         if live_stream is not None:
#             live_stream_data = format_video_data(live_stream)  
#             return jsonify(live_stream_data)
#         else:
#             return jsonify({"error": "No video at index"}), 404
#     except Exception as e:
#         return jsonify({"error": "Error occurred: {}".format(str(e))}), 500


@videos_blueprint.route("/live_streams/range", methods=["GET"])
def get_live_streams_range():
    try:
        start = request.args.get('start', default = 0, type = int)
        count = request.args.get('count', default = 10, type = int)
        
        live_streams = VideoService.get_live_streams_range(start, count)
        live_stream_data = format_videos_data(live_streams)
        table_length = VideoService.get_total_live_streams()
        lastPage = False
        if start+count >= table_length:
            lastPage = True
        return jsonify({
            "data":live_stream_data,
            "lastPage":lastPage
        })
    except Exception:
        return jsonify({"error":"ServerError"}), 500