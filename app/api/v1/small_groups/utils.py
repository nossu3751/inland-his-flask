from app.models.small_group import SmallGroup, Member

def format_small_group_data(small_group:SmallGroup):
    return {
        'id':small_group.id,
        'name':small_group.name,
        'members':[format_member_data(member) for member in small_group.members],
        'room':small_group.room
    }

def format_member_data(member:Member):
    return {
        'id': member.id,
        'name': member.name,
        'sub': member.sub,
        'is_leader': member.is_leader,
        'small_group_id': member.small_group_id
    }

def format_small_groups_data(small_groups):
    return [format_small_group_data(small_group) for small_group in small_groups]
