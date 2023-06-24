from sqlalchemy.orm import Session
from app.models import MdlUsers, MdlRoles
from sqlalchemy.orm.exc import NoResultFound
import sys

class UserService:
    def get_user(self, user_id: int, db: Session):
        try:
            u_record = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
            if u_record is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "user records not found."
                }
            
            elif u_record.role_id == 1:
                return {    "userId": u_record.id,
                            "firstName": u_record.fname,
                            "lastName": u_record.lname,
                            "emaildId": u_record.email,
                            "phoneNumber": u_record.number,
                            "password": u_record.password,
                            "active": u_record.is_active,
                            "roleId": u_record.role_id,
                            "parentUserId": u_record.parent_user_id }
            
            elif u_record.role_id == 2:
                users_list = []
                associated_users_record = db.query(MdlUsers).filter(MdlUsers.parent_user_id == user_id).all()
                for user_record in associated_users_record:
                    users_list.append({ "userId": user_record.id,
                                        "firstName": user_record.fname,
                                        "lastName": user_record.lname,
                                        "emaildId": user_record.email,
                                        "phoneNumber": user_record.number,
                                        "password": user_record.password,
                                        "active": user_record.is_active,
                                        "roleId": user_record.role_id,
                                        "parentUserId": user_record.parent_user_id })
                return users_list
            elif u_record.role_id == 3:
                users_list = []
                associated_users_record = [{ "userId": record.id,
                                            "firstName": record.fname,
                                            "lastName": record.lname,
                                            "emaildId": record.email,
                                            "phoneNumber": record.number,
                                            "password": record.password,
                                            "active": record.is_active,
                                            "roleId": record.role_id,
                                            "parentUserId": record.parent_user_id 
                                            } for record in db.query(MdlUsers).order_by(MdlUsers.id).all()]
                return associated_users_record
            
            
            
        except Exception as e:
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            # status_code = getattr(exc_value, "status_code", 500)  # Default to 500 if status_code is not present
            return {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"Internal Server Error: {e}"
            }

    def create_user(self, parent_user_id, fname, lname, email, number, password, is_active, role_id, db: Session):
        try:
            check_parent_id = db.query(MdlUsers).filter(MdlUsers.id==parent_user_id).one_or_none()
            if check_parent_id is None:
                return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "User_id not found"
            }
            check_role_id = db.query(MdlRoles).filter(MdlRoles.id==role_id).one_or_none()
            if check_role_id is None:
                return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "role_id not found"
            }
            db_user = MdlUsers(fname=fname, lname=lname, email=email, number=number, \
                            password=password, is_active=is_active, role_id=role_id, parent_user_id= parent_user_id)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "user has created successfully"
                }
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            status_code = getattr(exc_value, "status_code", 404)  # Default to 404 if status_code is not present
            return {
                "confirmMessageID": "string",
                "statusCode": status_code,
                "userMessage": f"unable to create the record : {e}"
            }

    def update_user(self, user_id:int, id: int, fname, lname, email, number, password, is_active, role_id, db: Session):
        try:
            user_id_re = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
            if user_id_re is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "Record not found."
                }

            db_user = db.query(MdlUsers).filter(MdlUsers.id == id).one()
            db_user.fname = fname
            db_user.lname = lname
            db_user.email = email
            db_user.number = number
            db_user.password = password
            db_user.is_active = is_active
            db_user.role_id = role_id
            db.commit()
            db.refresh(db_user)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "User updated successfully."
            }
        
        except NoResultFound:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "User not found."
            }
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            status_code = getattr(exc_value, "status_code", 500)  # Default to 500 if status_code is not present
            return {
                "confirmMessageID": "string",
                "statusCode": status_code,
                "userMessage": f"Internal Server Error: {e}"
            }


    def delete_user(self, user_id: int, db: Session):
        try:
            db_user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one()
            db.delete(db_user)
            db.commit()
            # delete from ilt, meetings, meeting responce
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "User deleted successfully."
            }
        except NoResultFound:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "User not found."
            }
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            status_code = getattr(exc_value, "status_code", 500)  # Default to 500 if status_code is not present
            return {
                "confirmMessageID": "string",
                "statusCode": status_code,
                "userMessage": f"Internal Server Error: {e}"
            }
