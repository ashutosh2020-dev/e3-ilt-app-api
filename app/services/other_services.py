from sqlalchemy.orm import Session
from app.models import MdlRoles, MdlUsers, MdlSchools, MdlPriorities
import sys

class Create_otherService:
    def create_root_user(self, fname, lname, email, number, password, is_active, role_id, db: Session):
        try:
            db_user = MdlUsers(fname=fname, lname=lname, email=email, number=number, \
                            password=password, is_active=is_active, role_id=role_id, parent_user_id= 0)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "root user has created successfully"
                }
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            status_code = getattr(exc_value, "status_code", 404)  # Default to 404 if status_code is not present
            return {
                "confirmMessageID": "string",
                "statusCode": status_code,
                "userMessage": f"unable to create the record : {e}"
            }
    def create_schools(self, name, location, district, db:Session):
        db_school = MdlSchools(name=name, location=location, district=district)
        db.add(db_school)
        db.commit()
        db.refresh(db_school) 
        return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "school has created successfully."
                }
    
    def create_roles(self, role_name:str, roleDescription:str, db:Session):
        db_role = MdlRoles(name=role_name, description=roleDescription)
        db.add(db_role)
        db.commit()
        db.refresh(db_role) 
        return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "role has created successfully."
                }

    def create_priority(self, name, description, db:Session):
        try:
            db_priority = MdlPriorities(name=name, description=description)
            db.add(db_priority)
            db.commit()
            db.refresh(db_priority)

            return {
                    "confirmMessageID": "string",
                    "statusCode": 200,
                    "userMessage": "priority has created."
                    }
        except Exception as e:
            return {
                    "confirmMessageID": "string",
                    "statusCode": 500,
                    "userMessage": f"unable to process your request. error - {e}"
                    }
