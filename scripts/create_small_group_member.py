import traceback
import requests, os, sys
sys.path.append(f'{sys.path[0]}/..')
from app import create_app
from app.extensions import db
from app.models.small_group import SmallGroup, Member
from app.api.v1.persons.services import PersonService
from app.api.v1.small_groups.services import SmallGroupService


def main():
    try:
        app = create_app()
        with app.app_context():
            persons = PersonService.get_persons()
            print(persons)
            for person_data in persons:
                try:
                    member_data = SmallGroupService.person_to_member(person_data)
                    SmallGroupService.create_member(member_data)
                    print(f"{member_data['name']} created.")
                except Exception as e:
                    print(f"creating member {person_data['id']} failed with error {e}")
    except Exception as e:
        print(f"Creating members failed with error {e}")

if __name__ == "__main__":
    main()