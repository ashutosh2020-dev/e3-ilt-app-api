from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from app.schemas.meeting_response import MeetingResponse, Duedate, Createdate
from datetime import datetime
from typing import Annotated, Union


router = APIRouter()
IltMeetingResponceService = IltMeetingResponceService()
 

@router.get("/api/v1/ilts/meetingResponses/{meetingResponseId}")
def read_meeting_responce_details(user_id: int, meetingResponseId:int,  db: Session = Depends(get_db)):
    return IltMeetingResponceService.get_Ilts_meeting_list(user_id=user_id, meetingResponseId=meetingResponseId, db=db)

@router.get("/api/v1/ilts/{id}/rocks")
def read_ilt_rocks(user_id:int, id:int, db: Session = Depends(get_db)):
    return IltMeetingResponceService.read_ilt_rock(user_id=user_id, ilt_id=id, db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/create_rocks")
def create_ilt_rocks(user_id: int, name: str, description:str,Ilt_id:int, db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_ilts_rocks(user_id=user_id, name=name,
                                                        description=description, Ilt_id=Ilt_id, db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/assign_rocks")
def assign_ilt_rocks_to_user(logged_user_id: int, user_id:int, Ilt_id:int, rock_id:int, db: Session = Depends(get_db)):
    return IltMeetingResponceService.assign_ilts_rocks(user_id=user_id, Ilt_id=Ilt_id,rock_id=rock_id, db=db)

@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/rocks")
def assign_ilt_rocks_to_meetingResponse(user_id: int, meetingResponseId:int, rock_id: int, onTrack:bool, db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_ilts_meeting_rocks(user_id= user_id, meetingResponseId= meetingResponseId,
                                                                rockId= rock_id, onTrack = onTrack, db = db)

@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/todolist")
def create_ilt_meeting_todolist(user_id:int, meetingResposnceId:int, description:str, dueDate:Duedate, 
                       status:str , db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_to_do_list(user_id=user_id, meetingResponseId=meetingResposnceId, description=description, \
                          dueDate=dueDate.Duedate, status=status, db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/updates")
def create_ilt_meeting_updates(user_id:int, meetingResponseId:int, description:str, db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_meeting_update(user_id=user_id, meetingResponseId=meetingResponseId, description=description, db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/issues")
def create_ilt_meeting_issues(user_id:int, meetingResponseId: int, issue:str, priorityId:bool, 
                    created_at:Createdate,
                     resolves_flag:bool,
                     recognize_performance_flag:bool,
                     teacher_support_flag:bool,
                     leader_support_flag:bool,
                     advance_equality_flag:bool,
                     others_flag:bool,db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_issue(user_id=user_id, 
                     meetingResponseId=meetingResponseId, issue=issue, priority=priorityId, 
                     created_at = created_at.CreateAt,
                     resolves_flag=resolves_flag,
                     recognize_performance_flag=recognize_performance_flag,
                     teacher_support_flag=teacher_support_flag,
                     leader_support_flag=leader_support_flag,
                     advance_equality_flag=advance_equality_flag,
                     others_flag=others_flag,
                     db=db)

@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}")
async def update_meeting_response(ilt_data: MeetingResponse, db: Session= Depends(get_db)):
    return IltMeetingResponceService.update_ilt_meeting_responses(data = ilt_data, db=db)
