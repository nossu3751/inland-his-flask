# from app.models.new_comer import NewComer

# def format_new_comer_data(new_comer:NewComer):
#     return {
#         'id': new_comer.id,
#         'name': new_comer.name,
#         'sermon_title': new_comer.sermon_title,
#         'sermon_subtitle': new_comer.sermon_subtitle,
#         'sermon_content': new_comer.sermon_content,
#         'representative_prayer': new_comer.representative_prayer,
#         'community_news': new_comer.community_news,
#         'message': new_comer.message,
#         'post_message_hymn': new_comer.post_message_hymn,
#         'blessing': new_comer.blessing,
#     }

# id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     birthday = db.Column(db.Date, nullable=False)
#     phone = db.Column(db.String, nullable=False)
#     p_address = db.Column(db.String, nullable=False)
#     m_address = db.Column(db.String, nullable=True)
#     email = db.Column(db.String, nullable=False)
#     baptized = db.Column(db.Boolean, nullable=False)

# def format_new_comers_data(new_comers):
#     return [format_new_comer_data(new_comer) for new_comer in new_comers]