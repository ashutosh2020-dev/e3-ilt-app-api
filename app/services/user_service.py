from sqlalchemy.orm import Session
from app.models import MdlUsers, MdlRoles
from sqlalchemy.orm.exc import NoResultFound
import sys
from app.exceptions.customException import CustomException
from app.schemas.user_schemas import UserAccount


class UserService:
    def get_user(self, user_id: int, db: Session):
        try:
            u_record = db.query(MdlUsers).filter(
                MdlUsers.id == user_id).one_or_none()
            if u_record is None:
                raise CustomException(404, "user records not found.")

            elif u_record.role_id == 1:
                return [{"userId": u_record.id,
                         "firstName": u_record.fname,
                         "lastName": u_record.lname,
                         "emailId": u_record.email,
                         "phoneNumber": u_record.number,
                         "password": u_record.password,
                         "active": u_record.is_active,
                         "roleId": u_record.role_id,
                         "parentUserId": u_record.parent_user_id}]

            elif u_record.role_id == 2:
                users_list = []
                user_query = db.query(MdlUsers).filter(
                    MdlUsers.parent_user_id == user_id)
                associated_users_record = user_query.all()
                for user_record in associated_users_record:
                    users_list.append({"userId": user_record.id,
                                       "firstName": user_record.fname,
                                       "lastName": user_record.lname,
                                       "emailId": user_record.email,
                                       "phoneNumber": user_record.number,
                                       "password": user_record.password,
                                       "active": user_record.is_active,
                                       "roleId": user_record.role_id,
                                       "parentUserId": user_record.parent_user_id})
                return users_list
            elif u_record.role_id == 3:
                users_list = []
                user_query = db.query(MdlUsers)
                associated_users_record = [{"userId": record.id,
                                            "firstName": record.fname,
                                            "lastName": record.lname,
                                            "emailId": record.email,
                                            "phoneNumber": record.number,
                                            "password": record.password,
                                            "active": record.is_active,
                                            "roleId": record.role_id,
                                            "parentUserId": record.parent_user_id
                                            } for record in user_query.order_by(MdlUsers.id).all()]
                return associated_users_record

        except Exception as e:
            raise CustomException(500,  f"Internal Server Error: {e}")

    def search_user(self, user_id: int, keyword: str, db: Session):
        u_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if u_record is None:
            raise CustomException(404, "user records not found.")

        elif u_record.role_id != 1:
            user_query = db.query(MdlUsers)
            if keyword:
                user_query = user_query.filter(MdlUsers.fname.like(f"%{keyword}%")
                                               | MdlUsers.lname.like(f"%{keyword}%"))
            associated_users_record = [UserAccount(record.id, record.fname, record.lname, record.role_id)
                                       for record in user_query.order_by(MdlUsers.id).all()]
            return associated_users_record

    def create_user(self, parent_user_id, fname, lname, email, number, password, is_active, role_id, db: Session):
        try:
            check_parent_id = db.query(MdlUsers).filter(
                MdlUsers.id == parent_user_id).one_or_none()
            if check_parent_id is None:
                raise CustomException(400,  "User_id not found")
            check_role_id = db.query(MdlRoles).filter(
                MdlRoles.id == role_id).one_or_none()
            if check_role_id is None:
                raise CustomException(400,  "role_id not found")
            db_user = MdlUsers(fname=fname, lname=lname, email=email, number=number,
                               password=password, is_active=is_active, role_id=role_id, parent_user_id=parent_user_id)
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
            # Default to 404 if status_code is not present
            status_code = getattr(exc_value, "status_code", 404)
            raise CustomException(500,  f"unable to create the record : {e}")

    def update_user(self, user_id: int, id: int, fname, lname, email, number, password, is_active, role_id, db: Session):
        try:
            user_id_re = db.query(MdlUsers).filter(
                MdlUsers.id == user_id).one_or_none()
            if user_id_re is None:
                raise CustomException(404,  "Record not found.")

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
            raise CustomException(400,  "User not found.")
        except Exception as e:
            raise CustomException(500,  f"Internal Server Error: {e}")

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
            raise CustomException(400,  "User not found.")
        except Exception as e:
            raise CustomException(500,  f"Internal Server Error: {e}")
