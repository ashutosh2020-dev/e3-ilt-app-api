from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_meeting_service import IltMeetingService
from datetime import datetime
from typing import Annotated, Union

router = APIRouter()
IltMeetingService = IltMeetingService()


@router.get("/api/v1/ilts/{id}/meetings")
def get_ilt_meetings(user_id: int, ilt_id: int, db: Session = Depends(get_db)):
    return IltMeetingService.get_Ilts_meeting_list(user_id = user_id, ilt_id = ilt_id, db =db )
    

@router.post("/api/v1/ilts/{id}/meetings")
def create_ilt_meeting(user_id:int, ilt_id:int, scheduledStartDate:Annotated[Union[datetime, None], Body()], 
                       meetingStart: Annotated[Union[datetime, None], Body()] , 
                       meetingEnd: Annotated[Union[datetime, None], Body()],location:str="" , db: Session = Depends(get_db)):
    return IltMeetingService.create_ilts_meeting(ilt_id=ilt_id, user_id=user_id, scheduledStartDate = scheduledStartDate, 
                       meetingStart = meetingStart, meetingEnd = meetingEnd, db=db, location = location)


@router.get("/api/v1/ilts/{id}/meetings/{meetingId}")
def get_meeting_info_wrt_meeting_id_and_ilt_id(User_id:int, id:int, meetingId:int, db: Session = Depends(get_db)):
    return IltMeetingService.get_meeting_info(meeting_id=meetingId, iltId = id, User_id =User_id, db = db)


# @router.post("/api/v1/ilts/{id}/meetings/{meetingId}")
# def update_ilt_meeting(user_id:int, meeting_id:int, scheduledStartDate:Annotated[Union[datetime, None], Body()], 
#                        meetingStart: Annotated[Union[datetime, None], Body()] , 
#                        meetingEnd: Annotated[Union[datetime, None], Body()], db: Session = Depends(get_db)):
#     return True