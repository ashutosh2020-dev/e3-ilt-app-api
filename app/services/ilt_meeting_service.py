from sqlalchemy.orm import Session
from app.models import MdlIltMeetings, MdlMeetings, MdlUsers

class IltMeetingService:
    def get_Ilts_meeting_list(self, user_id: int, ilt_id:int, db: Session):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
        if not user:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "User not found"
                }
        ilt_list = []
        list_meetings = [record.ilt_meeting_id for record in db.query(MdlIltMeetings).filter(MdlIltMeetings.ilt_id == ilt_id).all()]
        if list_meetings:
            for mid in list_meetings:
                meeting_record = db.query(MdlMeetings).filter(MdlMeetings.id == mid).first()
                val = {"iltId":ilt_id, "ilt_meeting_id":mid, "scheduledStartDate":meeting_record.meeting_schedule_start_at,
                        "meetingStart": meeting_record.meeting_start_at,"meetingEnd": meeting_record.meeting_end_at}
                ilt_list.append(val)
        return ilt_list

    def create_ilts_meeting(self, ilt_id: int,user_id:int,  scheduledStartDate, 
                       meetingStart, meetingEnd, db: Session, location:str):
        try:
            #check the user_id have relation with ilt_id
            db_meeting = MdlMeetings(location = location, schedule_start_at = scheduledStartDate, 
                                start_at = meetingStart, end_at = meetingEnd)
            db.add(db_meeting)
            db.commit()
            db.refresh(db_meeting)
            db_ilt_meeting = MdlIltMeetings(ilt_id = ilt_id, ilt_meeting_id = db_meeting.id)
            db.add(db_ilt_meeting)
            db.commit()
            db.refresh(db_ilt_meeting)
        except Exception as e:
            return  {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": "Internal Server Error = "+e
                }
        
        return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "meeting have successfully created"
            }
    
    def update_ilt_meeting(self, meeting_id: int, ilt_id: int,location, scheduledStartDate, meetingStart, 
                           meetingEnd,  db: Session):
        db_meeting = db.query(MdlMeetings).filter(MdlMeetings.id == meeting_id).first()
        if db_meeting:
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
                "statusCode": 500,
                "userMessage": "Internal Server Error"
                }
        
    def get_meeting_info(self, meeting_id:int, db:Session):
        db_meeting_record = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).first()
        if db_meeting_record:
            return {"meeting_id":db_meeting_record.id, "location":db_meeting_record.location, 
                   "schedule_start_at":db_meeting_record.schedule_start_at, 
                   "start_at":db_meeting_record.start_at,
                   "end_at":db_meeting_record.end_at}
        else:
            return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "enter valid meeting ID "
                }
            

