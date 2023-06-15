from app.models.bulletin import Bulletin, News, Hymn

def format_bulletin_data(bulletin:Bulletin):
    return {
        'id': bulletin.id,
        'sunday_date': bulletin.sunday_date.isoformat(),
        'sermon_title': bulletin.sermon_title,
        'sermon_subtitle': bulletin.sermon_subtitle,
        'sermon_content': bulletin.sermon_content,
        'representative_prayer': bulletin.representative_prayer,
        'community_news': bulletin.community_news,
        'message': bulletin.message,
        'post_message_hymn': bulletin.post_message_hymn,
        'blessing': bulletin.blessing,
        'news': [format_news_data(news) for news in bulletin.news],
        'hymns': [format_hymn_data(hymn) for hymn in bulletin.hymns],
    }

def format_news_data(news:News):
    return {
        'id': news.id,
        'title': news.title,
        'description': news.description
    }

def format_hymn_data(hymn:Hymn):
    return {
        'id': hymn.id,
        'title': hymn.title
    }

def format_bulletins_data(bulletins):
    return [format_bulletin_data(bulletin) for bulletin in bulletins]