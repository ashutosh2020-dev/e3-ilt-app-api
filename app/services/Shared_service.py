from sqlalchemy.orm import Session
from app.models import MdlIlts, MdlIltMembers, MdlUsers, MdlSchools
from app.models import MdlIltMeetingResponses, MdlMeeting_rocks, MdlRocks, MdlRoles, MdlIltPriorities, MdlUsers, MdlPriorities
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

class SharedService:
    def get_list_of_schools(self, user_id: int, db: Session):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
        if not user:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "User not found"
                }
        try:
            ilts_record = db.query(MdlIltMembers).filter(MdlIltMembers.member_id == user_id).all()
            school_id_list = []
            for record in ilts_record:
                ilt_school_id = db.query(MdlIlts).filter(MdlIlts.id == record.ilt_id).one().school_id
                school_id_list.append(ilt_school_id)

            school_id_list = list(set(school_id_list))

            ilt_schools_list = []

            for school in school_id_list:
                ilt_school_detail = db.query(MdlSchools).filter(MdlSchools.id == school).one()
                ilt_schools_list.append({
                    "schoolId" :  ilt_school_detail.id,
                    "schoolName" : ilt_school_detail.name,
                    "schoolDistrict" : ilt_school_detail.district})

            return ilt_schools_list
        
        except Exception as e:
            return {
            "confirmMessageID": "string",
            "statusCode": 500,
            "userMessage": f"Internal error {e}"
            }
        

    def get_list_of_rocks(self, user_id: int, db: Session):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
        if not user:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "User not found"
                }

        try:
            meeting_record = db.query(MdlIltMeetingResponses).filter(MdlIltMeetingResponses.meeting_user_id == user_id).all()
            meeting_response_id_list = []

            for record in meeting_record:
                meeting_response_id_list.append(record.meeting_response_id)

            rock_id_list = []    

            for response_id in meeting_response_id_list:
                rocks = db.query(MdlMeeting_rocks).filter(MdlMeeting_rocks.ilt_meeting_response_id == response_id).all()
                rock_ids = [rock.rock_id for rock in rocks]
                rock_id_list.extend(rock_ids)

            rock_id_list = list(set(rock_id_list))

            rock_details_list = []

            for rock_id in rock_id_list:
                rock_details = db.query(MdlRocks).filter(MdlRocks.id == rock_id).one()
                rock_details_list.append({
                    "rockId" : rock_details.id,
                    "description" : rock_details.description  
                })

            return rock_details_list    

        except Exception as e:
            return {
            "confirmMessageID": "string",
            "statusCode": 500,
            "userMessage": f"Internal error {e}"
            }  
       


    def get_role_details(self, user_id: int, db: Session):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
        if not user:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "User not found"
                }
        
        try:
            role_id = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()

            if not role_id:
                role_details = db.query(MdlRoles).filter(MdlRoles.id == role_id.role_id).first()

                return {
                    "roleId" : role_details.id,
                    "roleName" : role_details.name,
                    "roleDescription" : role_details.description
                }
            else:
                return {
                "confirmMessageID": "string",
                "statusCode": 0,
                "userMessage": "User not found"
                }
        
        except Exception as e:
            return {
            "confirmMessageID": "string",
            "statusCode": 500,
            "userMessage": f"Internal error {e}"
            }  
    def get_priority_details(self, UserId:int, db:Session):
        try:
            user_record = db.query(MdlUsers).filter(MdlUsers.id==UserId).one_or_none()
            if user_record is None:
                {
                    "confirmMessageID": "string",
                    "statusCode": 0,
                    "userMessage": "User not found"
                }
            user_priority_id_list = [record.priorities_id for record in db.query(MdlIltPriorities).filter(MdlIltPriorities.role_id==user_record.role_id).all()]
            priority_list = []
            for pid in user_priority_id_list:
                priority_record= db.query(MdlPriorities).filter(MdlPriorities.id==pid).one_or_none()
                priority_list.append({"priorityId":priority_record.id,"name":priority_record.name, "description":priority_record.description})
            return priority_list
        except Exception as e:
            return {
                 "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"Internal Error, unable to process your request {e}"
            }
    def get_lookup_details(self, user_id, db:Session):
        try:
            user_record = db.query(MdlUsers).filter(MdlUsers.id==user_id).one_or_none()
            if user_record is None:
                    {
                        "confirmMessageID": "string",
                        "statusCode": 0,
                        "userMessage": "User not found"
                    }
            ilts_record = db.query(MdlIltMembers).filter(MdlIltMembers.member_id == user_id).all()
            school_id_list = []
            for record in ilts_record:
                ilt_school_id = db.query(MdlIlts).filter(MdlIlts.id == record.ilt_id).one().school_id
                school_id_list.append(ilt_school_id)

            school_id_list = list(set(school_id_list))

            ilt_schools_list = []

            for school in school_id_list:
                ilt_school_detail = db.query(MdlSchools).filter(MdlSchools.id == school).one()
                ilt_schools_list.append({
                    "schoolId" :  ilt_school_detail.id,
                    "schoolName" : ilt_school_detail.name,
                    "schoolDistrict" : ilt_school_detail.district})

            
            meeting_record = db.query(MdlIltMeetingResponses).filter(MdlIltMeetingResponses.meeting_user_id == user_id).all()
            meeting_response_id_list = []

            for record in meeting_record:
                meeting_response_id_list.append(record.meeting_response_id)

            rock_id_list = []    

            for response_id in meeting_response_id_list:
                rocks = db.query(MdlMeeting_rocks).filter(MdlMeeting_rocks.ilt_meeting_response_id == response_id).all()
                rock_ids = [rock.rock_id for rock in rocks]
                rock_id_list.extend(rock_ids)

            rock_id_list = list(set(rock_id_list))

            rock_details_list = []

            for rock_id in rock_id_list:
                rock_details = db.query(MdlRocks).filter(MdlRocks.id == rock_id).one()
                rock_details_list.append({
                    "rockId" : rock_details.id,
                    "description" : rock_details.description  
                })

            return [{"roles":rock_details_list, "schools":ilt_schools_list}]
        except Exception as e:
            return {
                 "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"Internal Error, unable to process your request {e}"
            }
        