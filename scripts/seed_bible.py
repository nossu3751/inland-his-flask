import sys
sys.path.append(f'{sys.path[0]}/..')
print(sys.path)
import pandas as pd
from app import create_app
from app.extensions import db
from app.models.bible import Bible


def delete_all_bible():
    Bible.query.delete()
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        delete_all_bible()
        df = pd.read_csv("korean-bible.csv")
        for i in range(len(df)):
        
            book = df["book"].iloc[i]
            chapter = df["chapter"].iloc[i]
            verse = df["verse"].iloc[i]
            content = df["content"].iloc[i]
            book_name = df["bookName"].iloc[i]

            bible = Bible(
                book=int(book), 
                chapter=int(chapter), 
                verse=int(verse), 
                content=content, 
                book_name=book_name)
            print(bible)
            db.session.add(bible)
        db.session.commit()

