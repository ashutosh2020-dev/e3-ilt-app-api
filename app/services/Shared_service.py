# from sqlalchemy.orm import Session
# from app.models import MdlIlts, MdlIltMembers, MdlUsers, MdlSchools
# from sqlalchemy.exc import SQLAlchemyError
# from fastapi import HTTPException

# class SharedService:
#     def get_list_of_schools(self, user_id: int, db: Session):
#         user = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
#         if not user:
#             return {
#                 "confirmMessageID": "string",
#                 "statusCode": 404,
#                 "userMessage": "User not found"
#                 }
        
#         ilt_member_record = db.query(MdlIltMembers).filter(MdlIltMembers.member_id == user_id).all()
#         school_id_list = []
#         for i in ilt_member_record.ilt_id:
#             ilt_school_id = db.query(MdlIlts).filter(MdlIlts.id == ilt_member_record.ilt_id).one().school_id
#             school_id_list.append(ilt_school_id)

#         for i in school_id_list:



