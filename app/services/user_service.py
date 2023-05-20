from sqlalchemy.orm import Session
from app.models import MdlUsers
from sqlalchemy.orm.exc import NoResultFound
import sys

class UserService:
    def get_user(self, user_id: int, db: Session):
        try:
            user_record = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
            if user_record:
                return {
                            "userId": user_record.id,
                            "firstName": user_record.fname,
                            "lastName": user_record.lname,
                            "emaildId": user_record.email,
                            "phoneNumber": user_record.number,
                            "password": user_record.password,
                            "active": user_record.is_active,
                            "roleId": user_record.role_id,
                            "parent_user_Id": user_record.parent_user_id

                        }
            else:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "Record not found."
                }
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            status_code = getattr(exc_value, "status_code", 500)  # Default to 500 if status_code is not present
            return {
                "confirmMessageID": "string",
                "statusCode": status_code,
                "userMessage": f"Internal Server Error: {e}"
            }

    def create_user(self, parent_user_id, fname, lname, email, number, password, is_active, role_id, db: Session):
        try:
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
            print(status_code)
            return {
                "confirmMessageID": "string",
                "statusCode": status_code,
                "userMessage": f"unable to create the record : {e}"
            }

    def update_user(self, user_id: int, fname, lname, email, number, password, is_active, role_id, db: Session):
        try:
            db_user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one()
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
