import traceback
from app.models.small_group import SmallGroup, Member
from app.api.v1.small_groups.exceptions import *
from app.api.v1.persons.services import PersonService
from app.api.v1.small_groups.utils import format_members_data
from app.api.v1.persons.utils import separate_moeum
from app.extensions import db
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from jamo import j2hcj, h2j

class SmallGroupService:
    @staticmethod
    def get_all_small_groups():
        stmt = select(SmallGroup).order_by(SmallGroup.name.asc())
        return db.session.execute(stmt).scalars()

    
    @staticmethod
    def get_small_group_names_per_id():
        stmt = select(SmallGroup)
        small_groups = db.session.execute(stmt).scalars()
        return {small_group.id:small_group.name for small_group in small_groups}
    
    @staticmethod
    def get_all_members():
        stmt = select(Member).order_by(Member.name.asc())
        return db.session.execute(stmt).scalars()

    @staticmethod
    def get_member_by_id(id):
        stmt = select(Member).where(Member.id == id)
        return db.session.execute(stmt).scalar_one_or_none()
    
    @staticmethod
    def get_small_group_by_id(id):
        stmt = select(SmallGroup).where(SmallGroup.id == id)
        return db.session.execute(stmt).scalar_one_or_none()
    
    @staticmethod
    def get_small_group_by_name(name):
        stmt = select(SmallGroup).where(SmallGroup.name == name)
        return db.session.execute(stmt).scalar_one_or_none()
    
    @staticmethod
    def get_member_small_group(sub:str):
        print(sub)
        stmt = (select(Member)
                .where(Member.sub == sub)
                .options(joinedload(Member.small_group)))
        member = db.session.execute(stmt).scalar_one_or_none()
        print(member)
        return member.small_group if member else None
    
    @staticmethod
    def get_leaders(small_group_id=None):
        members = SmallGroupService.get_members_by_group_id(small_group_id)
        print(members)
        return [member for member in members if hasattr(member, "is_leader") and member.is_leader == True]

    @staticmethod
    def get_member_small_group_id(sub:str):
        stmt = (select(Member)
                .where(Member.sub == sub)
                .options(joinedload(Member.small_group)))
        member = db.session.execute(stmt).scalar_one_or_none()
        return member.small_group_id if member else None
    
    @staticmethod
    def update_member_sub(sub, member_id):
        member = db.session.query(Member).filter(Member.id == member_id).one_or_none()
        if member is None:
            raise MemberNotFoundException("Member with that id is not found")
        member["sub"] = sub
        db.session.commit()
        return member
    
    @staticmethod
    def update_member(member_id, updated_member_data):
        member = db.session.query(Member).filter(Member.id == member_id).one_or_none()
        if member is None:
            raise MemberNotFoundException("Member with that id is not found")
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
    def create_member(member_data):
        try:
            new_member = Member(**member_data)
            db.session.add(new_member)
            db.session.commit()
            return new_member
        except IntegrityError:
            db.session.rollback()
            raise MemberNotCreatedException("Failed to create member")
    
    @staticmethod 
    def update_small_group_members(small_group_id:int, members_data):
        print("update member service received this data", members_data)
        small_group = SmallGroupService.get_small_group_by_id(small_group_id)
        if small_group is None:
            raise SmallGroupNotFoundException("This small group not found")
        previous_members = small_group.members
        is_leader_present = False
        members = []
        for member_data in members_data:
            if "sub" in member_data and member_data["sub"] != None:
                sub = member_data["sub"]
                if member_data["is_leader"] == False:
                    PersonService.remove_from_cell_leader(sub)
                else:
                    PersonService.add_to_cell_leader(sub)
            member_small_group = member_data["small_group_id"]
            if member_small_group is not None and member_small_group != small_group_id:
                print("member small group id", member_small_group, "target small group id", small_group_id)
                print("member small group id type", type(member_small_group), "target small group id type", type(small_group_id))
                raise MemberCannotBeAddedException("This member is part of another small group")
            if "is_leader" in member_data and member_data["is_leader"] == True:
                is_leader_present = True
            if "id" not in member_data or member_data["id"] is None:
                member_data["small_group_id"] = small_group_id
                jamo_name = "".join(separate_moeum(c) for c in j2hcj(h2j(member_data["name"])))
                member_data["hangul_name"] = jamo_name
                try:
                    new_member = SmallGroupService.create_member(member_data)
                    members.append(new_member)
                except MemberNotCreatedException:
                    db.session.rollback()
                    raise SmallGroupMemberUpdateFailedException("Failed to create member")
            else:
                member_id = member_data["id"]
                member = SmallGroupService.get_member_by_id(member_id)
                if member is None:
                    db.session.rollback()
                    raise MemberNotFoundException("a member cannot be found in the current smallgroup. ")
                member.small_group_id = small_group_id
                member.is_leader = member_data["is_leader"]
                members.append(member)
        if len(members) > 0 and not is_leader_present :
            db.session.rollback()
            raise SmallGroupNoLeaderException("At least one leader needed")
        try:
            small_group.members = members
            member_ids = set([member.id for member in members])
            for prev_member in previous_members:
                if prev_member.id not in member_ids:
                    prev_member.small_group_id = None
            db.session.commit()
            return small_group
        except Exception:
            db.session.rollback()
            raise SmallGroupNotUpdatedException("Failed to update small group")

    @staticmethod
    def populate_small_group_members(members_data):
        is_leader_present = False
        try:
            db.session.commit()
            members = []
            for member_data in members_data:
                is_leader_present = member_data["is_leader"]

            if not is_leader_present:
                raise SmallGroupNoLeaderException("Small group needs leader")
            return members
        except IntegrityError:
            db.session.rollback()
            raise DuplicateMemberException("Member with same sub exists.")

    @staticmethod
    def create_small_group(small_group_data):
        try:
            is_leader_present = False
            members = []
            for member_data in small_group_data.pop("members", []):
                if "is_leader" in member_data and is_leader_present == False:
                    is_leader_present = member_data["is_leader"]
                members.append(Member(**member_data))
            if len(members) > 0 and not is_leader_present:
                raise SmallGroupNoLeaderException("At least one leader required")
            new_small_group = SmallGroup(members=members, **small_group_data)
            db.session.add(new_small_group)
            db.session.commit()
            return new_small_group
        except IntegrityError:
            db.session.rollback()
            raise DuplicateMemberException("Member with same sub exists.")
        except Exception:
            traceback.print_exc()
    
    @staticmethod
    def update_small_group_except_members(id, small_group_data):
        try:
            small_group = SmallGroupService.get_small_group_by_id(id)
            if small_group is None:
                    return None
            for p in small_group_data:
                if p != "members":
                    if hasattr(small_group, p):
                        setattr(small_group, p, small_group_data[p])
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise SmallGroupNotUpdatedException("small group update failed")

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
    def change_member_small_group(member_id:int, src_group_id:int, target_group_id:int):
        member = Member.query.get(member_id)
        src_group = SmallGroup.query.get(src_group_id)
        target_group = SmallGroup.query.get(target_group_id)

        if member is None:
            raise MemberNotFoundException("Member with that id is not found")
        
        if src_group is None or target_group is None:
            raise SmallGroupNotFoundException("Smallgroup with that id is not found")
    
        if member in src_group.members:
            src_group.members.remove(member)
        target_group.members.append(member)
        db.session.commit()

    @staticmethod
    def get_members_by_group_id(small_group_id=None):
        if not small_group_id:
            return SmallGroupService.get_all_members()
        stmt = select(Member).where(Member.small_group_id == small_group_id)   
        members = db.session.execute(stmt).scalars()
        print("found members", members)
        return members

    @staticmethod
    def get_members_by_group_name(group_name):
        # Retrieve the small group first
        group = SmallGroup.query.filter_by(name=group_name).first()

        # If no such group exists, return None or an empty list
        if not group:
            return None

        # Query the members associated with this small group
        members = Member.query.filter_by(small_group_id=group.id).all()

        return members

    @staticmethod
    def remove_member_from_small_group(member_id: int, group_id: int):
        # Find the existing member and group
        member = Member.query.get(member_id)
        group = SmallGroup.query.get(group_id)

        if member is None:
            raise MemberNotFoundException("Member with that id is not found")
        
        if group is None:
            raise SmallGroupNotFoundException("Smallgroup with that id is not found")
        
        # Remove the member from the group
        if member in group.members:
            group.members.remove(member)
            db.session.commit()

        return group
    
    @staticmethod
    def get_members_profile_photos(members=None):
        print(members)
        if members == None:
            members = format_members_data(SmallGroupService.get_all_members())
        members_profile_image_links = {member["id"]:None for member in members}
        try:
            persons_profile_image_links = PersonService.get_persons_profile_photos()
            # print(persons_profile_image_links)
            for member in members:
                member_id = member["id"]
                if "sub" in member:
                    sub = member["sub"]
                    if sub is not None and sub in persons_profile_image_links:
                        # print("does this work?")
                        try:
                            profile_link = persons_profile_image_links[sub]
                            members_profile_image_links[member_id] = profile_link
                            continue
                        except Exception:
                            continue
            return members_profile_image_links
        except Exception:
            return members_profile_image_links
        
    @staticmethod
    def person_to_member(person:dict):
        print(person)
        sub = person["id"]
        name = person["attributes"]["name"][0]
        hangul_name = person["attributes"]["hangul_name"][0]
        is_leader = False
        return {"name":name, "is_leader":is_leader, "sub":sub, "hangul_name":hangul_name}
    
    @staticmethod
    def search_member(search_str):
        results = db.session.query(Member).filter(Member.name.contains(search_str)).all()
        return results