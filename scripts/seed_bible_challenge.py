import sys
sys.path.append(f'{sys.path[0]}/..')
print(sys.path)
import pandas as pd
from app import create_app
from app.extensions import db
from app.models.bible_challenge import BibleChallenge
from dateutil.parser import parse

def delete_all_bible_challenge():
    BibleChallenge.query.delete()
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        delete_all_bible_challenge()
        df = pd.read_csv("bible-challenge.csv")
        for i in range(len(df)):
            date = df["date"].iloc[i]
            title = df["title"].iloc[i]
            book = df["book"].iloc[i]
            chapter = df["chapter"].iloc[i]
            if pd.isnull(book):
                book = None
            if pd.isnull(title):
                title = None
            if pd.isnull(chapter):
                chapter = None  # This will be inserted as NULL in the database
            else:
                chapter = int(chapter)  # Ensure chapter is an integer if it's not NaN


            print(chapter)

            bible_challenge = BibleChallenge(
                date=date,
                title=title,
                book=book,
                chapter=chapter
            )
          
            db.session.add(bible_challenge)
        db.session.commit()

