from fastapi import APIRouter, Depends, Body, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_meeting_service import IltMeetingService
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from app.schemas.ilt_meeting_schemas import MeetingData, rockData, rockData_map
from datetime import datetime
from typing import Annotated, Union

router = APIRouter()
IltMeetingService = IltMeetingService()
IltMeetingResponceService = IltMeetingResponceService()

@router.get("/api/v1/ilts/{id}/meetings")
def get_ilt_meetings( iltId: int, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingService.get_Ilts_meeting_list(user_id = UserId, ilt_id = iltId, db =db )
    

@router.post("/api/v1/ilts/{id}/meetings")
def create_ilt_meeting( id:int, ilt:MeetingData, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingService.create_ilts_meeting(ilt_id=id, 
                                                 user_id=UserId, 
                                                 scheduledStartDate = ilt.scheduledStartDate, 
                                                 meetingStart = ilt.meetingStart, 
                                                 meetingEnd = ilt.meetingEnd, 
                                                 location = ilt.location, 
                                                 db=db)


@router.get("/api/v1/ilts/{id}/meetings/{meetingId}")
def get_meeting_info_wrt_meeting_id_and_ilt_id(id:int, meetingId:int, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingService.get_meeting_info(meeting_id=meetingId, iltId = id, User_id =UserId, db = db)


# @router.post("/api/v1/ilts/{id}/meetings/{meetingId}")
# def update_ilt_meeting(user_id:int, meeting_id:int, scheduledStartDate:Annotated[Union[datetime, None], Body()], 
#                        meetingStart: Annotated[Union[datetime, None], Body()] , 
#                        meetingEnd: Annotated[Union[datetime, None], Body()], db: Session = Depends(get_db)):
#     return True

@router.get("/api/v1/ilts/{id}/rocks")
def read_ilt_rocks(id:int, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingResponceService.read_ilt_rock(user_id=UserId, ilt_id=id, db=db)


@router.post("/api/v1/ilts/meeting/create_rocks")
def create_ilt_rocks(rock:rockData, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_ilts_rocks(user_id=UserId, 
                                                       name=rock.name,
                                                       description=rock.description, 
                                                       Ilt_id=rock.ilt_id, 
                                                       db=db)


@router.post("/api/v1/ilts/meeting/assign_rocks")
def assign_ilt_rocks_to_user(rock:rockData_map,
                             UserId: int=Header(convert_underscores=False),
                             db: Session = Depends(get_db)):
    return IltMeetingResponceService.assign_ilts_rocks(logged_user_id=UserId,
                                                       user_id=rock.user_id, 
                                                       Ilt_id=rock.Ilt_id,
                                                       rock_id=rock.rock_id, 
                                                       db=db)
