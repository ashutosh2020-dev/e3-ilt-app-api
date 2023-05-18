from sqlalchemy.orm import Session
from app.models import MdlIltMeetings, MdlMeetings, MdlMeeting_rocks, MdlIlt_ToDoTask, Mdl_updates
from datetime import datetime
from typing import Annotated, Union


class IltMeetingResponceService:
    def get_Ilts_meeting_list(self, user_id: int, ilt_id:int, db: Session):
        return True #ilt_list


    def create_ilts_rocks(self, name: str, description:str,  scheduledStartDate, 
                       meetingStart, meetingEnd, db: Session, location:str):
        return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "meeting have successfully created"
            }
    

    def create_ilts_meeting_rocks(self, user_id: int, meetingResponseId:int, rockId:int, 
                       onTrack:bool, db: Session):
        try:
            # check if user_id is inside MdlIltMembers
            db_meeting_rocks = MdlMeeting_rocks(ilt_meeting_response_id = meetingResponseId, 
                                                rock_id=rockId, on_track_flag=onTrack)
            db.add(db_meeting_rocks)
            db.commit()
            db.refresh(db_meeting_rocks)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "user added successfully"
                }
        except Exception as e:
            return {
                "confirmMessageID": "string",
                "statusCode": 0,
                "userMessage": "unable to process your request "+ e
                }
    
    def create_to_do_list(user_id:int, meetingResponseId: int, description:str, 
                          dueDate, status:bool, db:Session):
        try:
            # check if user_id is inside MdlIltMembers
            db_meeting_rocks = MdlIlt_ToDoTask(response_id = meetingResponseId, 
                                                description=description, due_date=dueDate, status=status)
            db.add(db_meeting_rocks)
            db.commit()
            db.refresh(db_meeting_rocks)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "to-do list created successfully"
                }
        except Exception as e:
            return {
                "confirmMessageID": "string",
                "statusCode": 0,
                "userMessage": "unable to process your request "+ e
                }
    def create_meeting_update(user_id:int, meetingResponseId: int, description:str, db:Session):
        try:
            # check if user_id is inside MdlIltMembers
            db_meeting_update = Mdl_updates(response_id = meetingResponseId, 
                                                description=description)
            db.add(db_meeting_update)
            db.commit()
            db.refresh(db_meeting_update)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "to-do list created successfully"
                }
        except Exception as e:
            return {
                "confirmMessageID": "string",
                "statusCode": 0,
                "userMessage": "unable to process your request "+ e
                }
    
    def create_issue(user_id:int, meetingResponseId: int, description:str, db:Session):
        try:
            # check if user_id is inside MdlIltMembers
            db_meeting_update = Mdl_updates(response_id = meetingResponseId, 
                                                description=description)
            db.add(db_meeting_update)
            db.commit()
            db.refresh(db_meeting_update)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "to-do list created successfully"
                }
        except Exception as e:
            return {
                "confirmMessageID": "string",
                "statusCode": 0,
                "userMessage": "unable to process your request "+ e
                }
    # def update_ilt_meeting(self, meeting_id: int, ilt_id: int,location, scheduledStartDate, meetingStart, 
    #                        meetingEnd,  db: Session):
    #     try:
    #         db_meeting_rock = db.query(MdlMeeting_rocks).filter(MdlMeeting_rocks.rock_id == rockId).first()
    #         if db_meeting_rock:
    #             db_meeting_rock.ilt_meeting_response_id = meetingResponseId
    #             db_meeting_rock.rock_id = rockId 
    #             db_meeting_rock.on_track_flag = onTrack
    #             db.commit()
    #             db.refresh(db_meeting)
    #             return {
    #                     "confirmMessageID": "string",
    #                     "statusCode": 200,
    #                     "userMessage": "meeting have successfully created"
    #                     }
    #         else:
    #             return {
    #                 "confirmMessageID": "string",
    #                 "statusCode": 500,
    #                 "userMessage": "Internal Server Error"
    #                 }
    #     except Exception as e:
    #         return  {
    #             "confirmMessageID": "string",
    #             "statusCode": 500,
    #             "userMessage": "Internal Server Error = "+e
    #             }
        
    #     return {
    #             "confirmMessageID": "string",
    #             "statusCode": 200,
    #             "userMessage": "meeting have successfully created"
    #         }


    # def get_meeting_info(self, meeting_id:int, db:Session):
    #     db_meeting_record = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).first()
    #     if db_meeting_record:
    #         return {"meeting_id":db_meeting_record.id, "location":db_meeting_record.location, 
    #                "schedule_start_at":db_meeting_record.schedule_start_at, 
    #                "start_at":db_meeting_record.start_at,
    #                "end_at":db_meeting_record.end_at}
    #     else:
    #         return {
    #             "confirmMessageID": "string",
    #             "statusCode": 404,
    #             "userMessage": "enter valid meeting ID "
    #             }
            

