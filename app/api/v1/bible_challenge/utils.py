from app.models.bible_challenge import BibleChallenge
from app.models.bible import Bible

def format_bible_challenge_data(bible_challenge:BibleChallenge):
    return {
        'id': bible_challenge.id,
        'date': bible_challenge.date.isoformat(),
        'title': bible_challenge.title,
        'book': bible_challenge.book,
        'chapter': bible_challenge.chapter
    }


def format_bible_challenges_data(bible_challenges):
    return [format_bible_challenge_data(bible_challenge) for bible_challenge in bible_challenges]

def format_bible_verse(bible_verse:Bible):
    print(bible_verse)
    return {
        # 'id': bible_verse.id,
        'book': bible_verse.book,
        'book_name': bible_verse.book_name,
        'chapter': bible_verse.chapter,
        'verse': bible_verse.verse,
        'content': bible_verse.content
    }

def format_bible_verses(bible_verses):
    # for verse in bible_verses[0]:
    #     print(verse)
    return [format_bible_verse(bible_verse) for bible_verse in bible_verses]

