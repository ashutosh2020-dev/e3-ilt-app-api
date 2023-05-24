from sqlalchemy.orm import Session
from app.models import MdlIltMeetings, MdlMeetings, MdlUsers, MdlIlts, MdlIltMembers, MdlIltMeetingResponses, MdlMeetingsResponse
import sys
from app.services.ilt_meeting_response_service import IltMeetingResponceService


class IltMeetingService:
    def get_Ilts_meeting_list(self, user_id: int, ilt_id:int, db: Session):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
        if not user:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "User not found"
                }
        check_ilt = db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none()
        if check_ilt is None:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "Ilt not found"
                }
        list_meetings = [record.ilt_meeting_id for record in db.query(MdlIltMeetings).filter(MdlIltMeetings.ilt_id == ilt_id).all()]
        if len(list_meetings)>0:
            ilt_list = []
            for mid in list_meetings:
                meeting_record = db.query(MdlMeetings).filter(MdlMeetings.id == mid).first()
                val = {"iltId":ilt_id, "ilt_meeting_id":mid, "scheduledStartDate":meeting_record.schedule_start_at,
                        "meetingStart": meeting_record.start_at,"meetingEnd": meeting_record.end_at}
                ilt_list.append(val)

            return ilt_list
        else:
            return {
        "confirmMessageID": "string",
        "statusCode": 404,
        "userMessage": "No meeting available for this Ilt id"
        }

    def create_ilts_meeting(self, ilt_id: int,user_id:int,  scheduledStartDate, 
                       meetingStart, meetingEnd, db: Session, location:str):
        try:
            # check the user_id have relation with ilt_id
            user_record = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
            if user_record is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "User not found"
                    }
            Ilt_record = db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none()
            if Ilt_record is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "ILT not found"
                    }
            db_meeting = MdlMeetings(location = location, schedule_start_at = scheduledStartDate, 
                                start_at = meetingStart, end_at = meetingEnd)
            db.add(db_meeting)
            db.commit()
            db.refresh(db_meeting)

            ilt_members_list = [record.member_id for record in db.query(MdlIltMembers).filter(MdlIltMembers.ilt_id==ilt_id).all()]
            print(ilt_members_list)
            # create meeting response and update the map table(MdlIltMeetingResponses) for  meeting id and m_response_id
            status, msg = IltMeetingResponceService().create_meeting_responses_empty_for_ILTmember(meeting_id=db_meeting.id, \
                                                                                              member_list = ilt_members_list, db=db)
            if status is not True:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": f"Unable to create meeting responce : {msg}"
                    }
            # update map table about new ilt and ilt_meeting's relationship
            db_ilt_meeting = MdlIltMeetings(ilt_id = ilt_id, ilt_meeting_id = db_meeting.id, )
            db.add(db_ilt_meeting)
            db.commit()
            db.refresh(db_ilt_meeting)

        except Exception as e:
            return  {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"Internal Server Error: {e}"
                }
        
        return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "meeting and corresponding meeting_response have successfully created"
            }
    
    def update_ilt_meeting(self, meeting_id: int, ilt_id: int,location, scheduledStartDate, meetingStart, 
                           meetingEnd,  db: Session):
        try:
            db_meeting = db.query(MdlMeetings).filter(MdlMeetings.id == meeting_id).one_or_none()
            if db_meeting is not None:
                db_meeting.location = location
                db_meeting.schedule_start_at = scheduledStartDate
                db_meeting.start_at = meetingStart
                db_meeting.end_at = meetingEnd
                db.commit()
                db.refresh(db_meeting)
                return {
                        "confirmMessageID": "string",
                        "statusCode": 200,
                        "userMessage": "meeting have successfully created"
                        }
            else:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "records not found"
                    }
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            status_code = getattr(exc_value, "status_code", 404)  # Default to 404 if status_code is not present
            return {
                "confirmMessageID": "string",
                "statusCode": status_code,
                "userMessage": f"unable to create the record : {e}"
            }


    def get_meeting_info(self, User_id:int, iltId:int, meeting_id:int,  db:Session):
        try:
            user = db.query(MdlUsers).filter(MdlUsers.id == User_id).one_or_none()
            if user is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "User not found"
                    }
            db_ilt_meeting_record = db.query(MdlIltMeetings).filter(
                                MdlIltMeetings.ilt_id == iltId,
                                MdlIltMeetings.ilt_meeting_id == meeting_id
                            ).one_or_none()
            if db_ilt_meeting_record is not None:
                
                db_meeting_record = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one()
                # ilt_members_ids = [x.member_id for x in db.query(MdlIltMembers).filter(MdlIltMembers.ilt_id==iltId).all()]
                ilt_members_ids = [User_id]
                members_Info_dict = []
                meeting_response_id = 0
                for uid in ilt_members_ids:
                    user_record = db.query(MdlUsers).filter(MdlUsers.id==uid).one()
                    meeting_response_id = db.query(MdlIltMeetingResponses)\
                                            .filter(MdlIltMeetingResponses.meeting_id==meeting_id,
                                                    MdlIltMeetingResponses.meeting_user_id==uid).one().meeting_response_id
                    meeting_response_record = db.query(MdlMeetingsResponse)\
                                            .filter(MdlMeetingsResponse.id==meeting_response_id).one()
                    
                    members_Info_dict.append({"id":user_record.id,
                                                "first name":user_record.fname, 
                                                "last name":user_record.lname,
                                                "attandance":meeting_response_record.attendance_flag,
                                                "personalBest":meeting_response_record.checkin_personal_best,
                                                "professionalBest":meeting_response_record.checkin_professional_best,
                                                "rating":meeting_response_record.rating,
                                                "feedback":meeting_response_record.feedback,
                                                "notes":meeting_response_record.notes
                                                })
                # note - add rocks, issue, update, to-doList info 
                return {
                        "iltMeetingId":db_meeting_record.id,
                        "meeting_response_id":meeting_response_id,
                        "location":db_meeting_record.location, 
                        "schedule_start_at":db_meeting_record.schedule_start_at, 
                        "start_at":db_meeting_record.start_at,
                        "end_at":db_meeting_record.end_at, 
                        "member":members_Info_dict
                        }
            else:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "enter valid Meeting ID or ILT id"
                    }
        except Exception as e:
            return {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"Internal server error{str(e)}"
            }
            

