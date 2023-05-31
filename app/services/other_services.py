from sqlalchemy.orm import Session
from app.models import MdlRoles, MdlUsers, MdlSchools, MdlPriorities, MdlIltPriorities
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
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

    def create_priority(self, role_id, name, description, db:Session):
        check_role_record = db.query(MdlRoles).filter(MdlRoles.id==role_id).one_or_none()
        if check_role_record is None:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "roleid not found."
                }
        db_prioritie = MdlPriorities(name=name, description=description)
        db.add(db_prioritie)
        db.commit()
        db.refresh(db_prioritie)
        db_priority_map = MdlIltPriorities(role_id=role_id, priorities_id=db_prioritie.id)
        db.add(db_priority_map)
        db.commit()
        db.refresh(db_priority_map)

        return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "priority has created and added to the role_id successfully ."
                }

#     def create_role(self, name, description, db:Session):
#         try:
#             db_role = MdlRoles(name=name, description=description)
#             db.add(db_role)
#             db.commit()
#             db.refresh(db_role)
#             return {
#                 "confirmMessageID": "string",
#                 "statusCode": 200,
#                 "userMessage": "role has created successfully"
#                 }
#         except Exception as e:
#             exc_type, exc_value, exc_traceback = sys.exc_info()
#             status_code = getattr(exc_value, "status_code", 404)  # Default to 404 if status_code is not present
#             return {
#                 "confirmMessageID": "string",
#                 "statusCode": status_code,
#                 "userMessage": f"unable to create the record : {e}"
#             }

#     def create_school_record(self, name, location, district, db:Session):
#         try:
#             db_school = MdlSchools(name=name, location=location, district=district)
#             db.add(db_school)
#             db.commit()
#             db.refresh(db_school)
#             return {
#                 "confirmMessageID": "string",
#                 "statusCode": 200,
#                 "userMessage": "user has created successfully"
#                 }
#         except Exception as e:
#             exc_type, exc_value, exc_traceback = sys.exc_info()
#             status_code = getattr(exc_value, "status_code", 404)  # Default to 404 if status_code is not present
#             return {
#                 "confirmMessageID": "string",
#                 "statusCode": status_code,
#                 "userMessage": f"unable to create the record : {e}"
#             }

    
#     def create_root_user(self, parent_user_id, fname, lname, email, number, password, is_active, role_id, db:Session):
#         try:
#             if bool(db.query(MdlUsers).first()) != True:
#                 db_root_user = MdlUsers(fname=fname, lname=lname, email=email, number=number, \
#                                 password=password, is_active=is_active, role_id=role_id, parent_user_id= parent_user_id)
#                 db.add(db_root_user)
#                 db.commit()
#                 db.refresh(db_root_user)
#                 return {
#                     "confirmMessageID": "string",
#                     "statusCode": 200,
#                     "userMessage": "Root user's records has created successfully"
#                     }
#             else:
#                 return {
#                     "confirmMessageID": "string",
#                     "statusCode": 200,
#                     "userMessage": "Unable to process your request as 1 root user can be create only"
#                     }
#         except Exception as e:
#             exc_type, exc_value, exc_traceback = sys.exc_info()
#             status_code = getattr(exc_value, "status_code", 404)  # Default to 404 if status_code is not present
#             return {
#                 "confirmMessageID": "string",
#                 "statusCode": status_code,
#                 "userMessage": f"unable to create the record : {e}"
#             }
    
#     def create_priorities(self):
#         try:
#             db_user = MdlPriorities(fname=fname, lname=lname, email=email, number=number, \
#                             password=password, is_active=is_active, role_id=role_id, parent_user_id= parent_user_id)
#             db.add(db_user)
#             db.commit()
#             db.refresh(db_user)
#             return {
#                 "confirmMessageID": "string",
#                 "statusCode": 200,
#                 "userMessage": "user has created successfully"
#                 }
#         except Exception as e:
#             exc_type, exc_value, exc_traceback = sys.exc_info()
#             status_code = getattr(exc_value, "status_code", 404)  # Default to 404 if status_code is not present
#             return {
#                 "confirmMessageID": "string",
#                 "statusCode": status_code,
#                 "userMessage": f"unable to create the record : {e}"
#             }
#         return pass
     