from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from datetime import datetime
from typing import Annotated, Union

router = APIRouter()
IltMeetingResponceService = IltMeetingResponceService()


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/rocks")
def create_ilt_meetings_rocks(user_id: int, meetingResponseId:int, rock_id: int, onTrack, db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_ilts_meeting_rocks(user_id= user_id, meetingResponseId= meetingResponseId,
                                                                rockId= rock_id, onTrack = onTrack, db = db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/todolist")
def create_ilt_meeting_todolist(user_id:int, meetingResposnceId:int, description:str, dueDate:Annotated[Union[datetime, None], Body()], 
                       status:bool , db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_to_do_list(user_id=user_id, meetingResponseId=meetingResposnceId, description=description, 
                          dueDate=dueDate, status=status, db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/updates")
def create_ilt_meeting_updates(user_id:int, meetingResponseId:int, description:str, db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_meeting_update(user_id=user_id, meetingResponseId=meetingResponseId, description=description, db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/issues")
def create_ilt_meeting_issues(user_id:int, meetingResponseId:int, description:str,db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_issue(user_id=user_id, meetingResponseId=meetingResponseId, description=description, db=db)

