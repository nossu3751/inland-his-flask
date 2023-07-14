from app.models.small_group import SmallGroup, Member
from app.api.v1.small_groups.exceptions import *
from app.extensions import db
from sqlalchemy import select
from sqlalchemy.orm import joinedload

class SmallGroupService:
    @staticmethod
    def get_all_small_groups():
        stmt = select(SmallGroup).order_by(SmallGroup.name.asc())
        return db.session.execute(stmt).scalars()

    @staticmethod
    def get_small_group_by_id(id):
        stmt = select(SmallGroup).where(SmallGroup.id == id)
        return db.session.execute(stmt).scalar_one_or_none()
    
    @staticmethod
    def get_member_small_group(sub:str):
        stmt = (select(Member)
                .where(Member.sub == sub)
                .options(joinedload(Member.small_group)))
        member = db.session.execute(stmt).scalar_one_or_none()
        return member.small_group if member else None
    
    @staticmethod
    def get_member_small_group_id(sub:str):
        stmt = (select(Member)
                .where(Member.sub == sub)
                .options(joinedload(Member.small_group)))
        member = db.session.execute(stmt).scalar_one_or_none()
        return member.small_group_id if member else None
    
    @staticmethod
    def update_member(member_id, updated_member_data):
        member = db.session.query(Member).filter(Member.id == member_id).one_or_none()
        
        for field, value in updated_member_data.items():
            if hasattr(member, field):
                setattr(member, field, value)
        
        db.session.commit()
        return member
    
    @staticmethod
    def get_small_group_by_index(index):
        stmt = (select(SmallGroup)
                .order_by(SmallGroup.name.asc())
                .offset(index)
                .limit(1))
        return db.session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create_small_group(small_group_data):
        members = [Member(**member_data) for member_data in small_group_data.pop("members", [])]
        new_small_group = SmallGroup(members=members **small_group_data)
        db.session.add(new_small_group)
        db.session.commit()
        return new_small_group
    
    @staticmethod
    def update_small_group(id, small_group_data):
        small_group = SmallGroupService.get_small_group_by_id(id)
        if small_group is None:
                return None

        # Step 3: Update the desired fields of the object
        for field, value in small_group_data.items():
            if field != "members":
                if hasattr(small_group, field):
                    setattr(small_group, field, value)
        
        db.session.commit()

    @staticmethod
    def add_member_to_small_group(member, small_group_id:int):
        sub = member["sub"] if "sub" in member else None
        small_group = SmallGroupService.get_small_group_by_id(small_group_id)
        if sub is None:
            small_group.members.append(member)
            db.session.commit()
            return small_group
        member = db.session.query(Member).filter(Member.sub == sub).one_or_none()
        if member is None:
            small_group.members.append(member)
            db.session.commit()
            return small_group
        member_small_group_id = SmallGroupService.get_member_small_group_id(sub)
        if member_small_group_id == None:
            small_group.members.append(member)
            db.session.commit()
            return small_group
        else:
            raise MemberAlreadyAddedException("Member is already in another small group")

    @staticmethod
    def remove_member_from_small_group(member_id: int, group_id: int):
        # Find the existing member and group
        member = Member.query.get(member_id)
        group = SmallGroup.query.get(group_id)

        # Make sure both exist
        if member is None or group is None:
            return None

        # Remove the member from the group
        if member in group.members:
            group.members.remove(member)
            db.session.commit()

        return group
    
    