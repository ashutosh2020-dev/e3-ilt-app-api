from sqlalchemy.orm import Session
from app.models import MdlIlts, MdlIltMembers, MdlUsers, MdlSchools
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

class IltService:
    def get_Ilts_list(self, user_id: int, db: Session):
        ilt_list = []
        list_ilts = [record.ilt_id for record in db.query(MdlIltMembers).filter(MdlIltMembers.member_id == user_id).all()]
        print(list_ilts)
        if list_ilts:
            for x in list_ilts:
                ilt_record = db.query(MdlIlts).filter(MdlIlts.id == x).first()
                ilt_owner_record = db.query(MdlUsers).filter(MdlUsers.id == ilt_record.owner_id).first()
                owner_name = ilt_owner_record.fname+" "+ilt_owner_record.lname
                val = {"itlId":ilt_record.id, "title":ilt_record.title, "description": ilt_record.description, "owner name":owner_name}
                ilt_list.append(val)
            return ilt_list
        return {
        "confirmMessageID": "string",
        "statusCode": 0,
        "userMessage": "records Not found"
        }
    def get_ilt_details(self, ilt_id:int, db:Session):
        try:
            ilt_record = db.query(MdlIlts).filter(MdlIlts.id==ilt_id).one()
            members_id_list = [record.id for record in db.query(MdlIltMembers).filter(MdlIltMembers.ilt_id==ilt_id).all()]
            school_record = db.query(MdlSchools).filter(MdlSchools.id==ilt_record.school_id).first()
            owner_record = db.query(MdlUsers).filter(MdlUsers.id==ilt_record.owner_id).one()
            member_info = []
            for uid in members_id_list:
                user_record = db.query(MdlUsers).filter(MdlUsers.id==uid).one()
                member_info.append({"user_id":user_record.id,"first_name":user_record.fname, "last_name":user_record.lname})
            return {
                    "itlId": ilt_record.id,
                    "onwer": {
                        "userId": owner_record.id,
                        "firstName": owner_record.fname,
                        "lastName": owner_record.lname
                    },
                    "tile": ilt_record.title,
                    "description": ilt_record.description,
                    "school": {
                        "schoolId": 0,
                        "schoolName": "string",
                        "schoolDistrict": "string"
                    },
                    "members": member_info
                    }
        except Exception as e:
            
            return None
    
    def is_user_exist(self, user_id, db):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        if user is not None:
            return True
        else:
            return False

    def create_ilts(self, owner_id, title, description, school_id, member_id_list, db: Session):
        try:
            # validate school id existance
            #validate owner id 
            user = db.query(MdlUsers).filter(MdlUsers.id == owner_id).first()
            if not user:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "User not found"
                    }
            db_ilt = MdlIlts(owner_id = owner_id, title= title, description= description, school_id= school_id)
            db.add(db_ilt)
            db.commit()
            db.refresh(db_ilt)
            print(db_ilt.id)
            # mapping all user's id with ilt in the map table also check uid existance
            for m_id in member_id_list:
                # flag = self.is_user_exist(user_id = m_id, db=db)
                db_user_id = db.query(MdlUsers).filter(MdlUsers.id == m_id).first().id
                db_ilt_member = MdlIltMembers(ilt_id = db_ilt.id, member_id = db_user_id)
                db.add(db_ilt_member)
                db.commit()
                db.refresh(db_ilt_member)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "created successfully"
                }
        except SQLAlchemyError as e:
            # db.rollback()
            return {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"Failed to store data in the database. Error: {str(e)}"
                }
        except Exception as e:
            # db.rollback()
            return {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"unable to process your request: {str(e)}"
                }



    # def update_ilt(self,ilt_id:int, user_id:int, title: str, description: str, 
    #                  school_id: int, member_id: list ,db: Session):
    #     # check user_id?
    #     db_user = db.query(MdlIlts).filter(MdlIlts.id == ilt_id).first()
    #     if db_user: 
    #         db_user.fname = fname
    #         db_user.lname = lname
    #         db_user.email = email
    #         db_user.number = number
    #         db_user.password = password
    #         db_user.is_active = is_active
    #         db_user.role_id = role_id
    #         db.commit()
    #         db.refresh(db_user)
    #         return True
    #     else:
    #         return False

