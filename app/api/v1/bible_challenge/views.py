from flask import Blueprint, jsonify, request, abort
from app.api.v1.bible_challenge.services import BibleChallengeService
from app.api.v1.bible_challenge.utils import *
from datetime import datetime, timedelta
import traceback

bible_challenges_blueprint = Blueprint('bible_challenges', __name__, url_prefix="/api/v1/bible_challenges")

@bible_challenges_blueprint.route('/', methods=['GET'])
def get_bible_challenges():
    try:
        bible_challenges = BibleChallengeService.get_all_bible_challenges()
        return jsonify(format_bible_challenges_data(bible_challenges)), 200
    except Exception:
        traceback.print_exc()
        return jsonify({"error":"failed to get bible challeges"}), 404
    
@bible_challenges_blueprint.route('/<date>', methods=['GET'])
def get_bible_verses_by_challenge_date(date):
    try:
        bible_verses, book, chapter = BibleChallengeService.get_bible_verses_by_challenge_date(date)
        if bible_verses:
            return jsonify({
                "verses":format_bible_verses(bible_verses),
                "date":date,
                "book":book,
                "chapter":chapter
            })
        else:
            raise Exception
    except Exception:
        traceback.print_exc()
        return jsonify({"error":"failed to get bible verses"}), 404

@bible_challenges_blueprint.route("/<book_name>/<chapter>", methods=['GET'])
def get_bible_verses(book_name, chapter):
    try:
        bible_verses = BibleChallengeService.get_bible_verses(book_name, chapter)
        print(bible_verses)
        return jsonify(bible_verses), 200
    except Exception:
        traceback.print_exc()
        return jsonify({"error":"failed to get bible verses"}), 404