from sqlalchemy.orm import Session
from app.models import MdlIlts, MdlIltMembers, MdlUsers, MdlSchools
from app.models import MdlIltMeetingResponses, MdlMeeting_rocks, MdlRocks,\
                MdlRoles, MdlIltPriorities, MdlUsers, MdlPriorities, MdlIltissue, Mdl_issue, MdlIlt_rocks
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

class SharedService:
    def get_list_of_schools(self,  db: Session):
        
        try:
            
            ilt_school_detail = [{
                                    "schoolId" :  ilt_school_detail.id,
                                    "schoolName" : ilt_school_detail.name,
                                    "schoolDistrict" : ilt_school_detail.district
                                 } for ilt_school_detail in db.query(MdlSchools).all()]

            return ilt_school_detail
        
        except Exception as e:
            return {
            "confirmMessageID": "string",
            "statusCode": 500,
            "userMessage": f"unable to process your requests {e}"
            }
        

    def get_list_of_rocks(self, db: Session):
        try:
            
            ilt_rock_details = [{
                                    "rockId" :  record.id,
                                    "description" : record.name,
                                 } for record in db.query(MdlRocks).all()]

            return ilt_rock_details
        
        except Exception as e:
            return {
            "confirmMessageID": "string",
            "statusCode": 500,
            "userMessage": f"unable to process your requests {e}"
            }   

    def get_list_of_ilt_rocks(self, iltId: int, db: Session):
        ilt_record = db.query(MdlIlts).filter(MdlIlts.id == iltId).one_or_none()
        if ilt_record is None:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "ilt does not exist"
                }
        try:
            # re = db.query(MdlIlt_rocks).filter(MdlIlt_rocks.ilt_rock_id == iltId).all()
            rock_records = (
                                db.query(MdlRocks)
                                .join(MdlIlt_rocks, MdlRocks.ilt_id == MdlIlt_rocks.ilt_id)
                                .filter(MdlRocks.ilt_id==iltId)
                                .all()
                            )
            ilt_rock_details = [{
                                    "schoolId" :  ilt_rock_detail.id,
                                    "schoolName" : ilt_rock_detail.name,
                                    "schoolDistrict" : ilt_rock_detail.district
                                 } for ilt_rock_detail in rock_records]

            return ilt_rock_details
        
        except Exception as e:
            return {
            "confirmMessageID": "string",
            "statusCode": 500,
            "userMessage": f"unable to process your requests {e}"
            } 


    def get_role_details(self,db: Session):
        try:
            roles = [{
                            "roleId": record.id,
                            "roleName": record.name,
                            "roleDescription": record.description
                        } for record in db.query(MdlRoles).all()]

            return roles
        
        except Exception as e:
            return {
            "confirmMessageID": "string",
            "statusCode": 500,
            "userMessage": f"unable to process your requests {e}"
            } 
        
    def get_priority_details(self, db:Session):
        try:
            priority = [{
                            "priorityId": record.id,
                            "name": record.name,
                            "description": record.description
                        } for record in db.query(MdlPriorities).all()]

            return priority
        
        except Exception as e:
            return {
            "confirmMessageID": "string",
            "statusCode": 500,
            "userMessage": f"unable to process your requests {e}"
            } 
    def get_lookup_details(self, db:Session):
        try:
            # user_record = db.query(MdlUsers).filter(MdlUsers.id==user_id).one_or_none()
            # if user_record is None:
            #         {
            #             "confirmMessageID": "string",
            #             "statusCode": 0,
            #             "userMessage": "User not found"
            #         }

            school_details = [{
                                    "schoolId" :  record.id,
                                    "schoolName" : record.name,
                                    "schoolDistrict" : record.district
                                 } for record in db.query(MdlSchools).all()]
            rock_details = [{
                                    "rockId" :  record.id,
                                    "description" : record.name,
                                 } for record in db.query(MdlRocks).all()]
            roles = [{
                            "roleId": record.id,
                            "roleName": record.name,
                            "roleDescription": record.description
                        } for record in db.query(MdlRoles).all()]
            
            priorities = [{
                            "priorityId": record.id,
                            "name": record.name,
                            "description": record.description
                        } for record in db.query(MdlPriorities).all()]

            return [ {"roles":roles,
                "priorities":priorities,
                "schools":school_details,
                "rocks": rock_details}
                ]
            
            # ilts_record = db.query(MdlIltMembers).filter(MdlIltMembers.member_id == user_id).all()
            # school_id_list = []
            # for record in ilts_record:
            #     ilt_school_id = db.query(MdlIlts).filter(MdlIlts.id == record.ilt_id).one().school_id
            #     school_id_list.append(ilt_school_id)

            # school_id_list = list(set(school_id_list))

            # ilt_schools_list = []

            # for school in school_id_list:
            #     ilt_school_detail = db.query(MdlSchools).filter(MdlSchools.id == school).one()
            #     ilt_schools_list.append({
            #         "schoolId" :  ilt_school_detail.id,
            #         "schoolName" : ilt_school_detail.name,
            #         "schoolDistrict" : ilt_school_detail.district})

            
            # meeting_record = db.query(MdlIltMeetingResponses).filter(MdlIltMeetingResponses.meeting_user_id == user_id).all()
            # meeting_response_id_list = []

            # for record in meeting_record:
            #     meeting_response_id_list.append(record.meeting_response_id)

            # rock_id_list = []    

            # for response_id in meeting_response_id_list:
            #     rocks = db.query(MdlMeeting_rocks).filter(MdlMeeting_rocks.ilt_meeting_response_id == response_id).all()
            #     rock_ids = [rock.rock_id for rock in rocks]
            #     rock_id_list.extend(rock_ids)

            # rock_id_list = list(set(rock_id_list))

            # rock_details_list = []

            # for rock_id in rock_id_list:
            #     rock_details = db.query(MdlRocks).filter(MdlRocks.id == rock_id).one()
            #     rock_details_list.append({
            #         "rockId" : rock_details.id,
            #         "description" : rock_details.description  
            #     })

            # return [{"roles":rock_details_list, "schools":ilt_schools_list}]
        except Exception as e:
            return {
                 "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"Internal Error, unable to process your request {e}"
            }
        