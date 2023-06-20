from fastapi import APIRouter, Depends, Body
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
def get_ilt_meetings(user_id: int, ilt_id: int, db: Session = Depends(get_db)):
    return IltMeetingService.get_Ilts_meeting_list(user_id = user_id, ilt_id = ilt_id, db =db )
    

@router.post("/api/v1/ilts/{id}/meetings")
def create_ilt_meeting(user_id:int, id:int, ilt:MeetingData, db: Session = Depends(get_db)):
    return IltMeetingService.create_ilts_meeting(ilt_id=id, 
                                                 user_id=user_id, 
                                                 scheduledStartDate = ilt.scheduledStartDate, 
                                                 meetingStart = ilt.meetingStart, 
                                                 meetingEnd = ilt.meetingEnd, 
                                                 location = ilt.location, 
                                                 db=db)


@router.get("/api/v1/ilts/{id}/meetings/{meetingId}")
def get_meeting_info_wrt_meeting_id_and_ilt_id(User_id:int, id:int, meetingId:int, db: Session = Depends(get_db)):
    return IltMeetingService.get_meeting_info(meeting_id=meetingId, iltId = id, User_id =User_id, db = db)


# @router.post("/api/v1/ilts/{id}/meetings/{meetingId}")
# def update_ilt_meeting(user_id:int, meeting_id:int, scheduledStartDate:Annotated[Union[datetime, None], Body()], 
#                        meetingStart: Annotated[Union[datetime, None], Body()] , 
#                        meetingEnd: Annotated[Union[datetime, None], Body()], db: Session = Depends(get_db)):
#     return True

@router.get("/api/v1/ilts/{id}/rocks")
def read_ilt_rocks(user_id:int, id:int, db: Session = Depends(get_db)):
    return IltMeetingResponceService.read_ilt_rock(user_id=user_id, ilt_id=id, db=db)


@router.post("/api/v1/ilts/meeting/create_rocks")
def create_ilt_rocks(user_id: int, rock:rockData, db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_ilts_rocks(user_id=user_id, 
                                                       name=rock.name,
                                                       description=rock.description, 
                                                       Ilt_id=rock.ilt_id, 
                                                       db=db)


@router.post("/api/v1/ilts/meeting/assign_rocks")
def assign_ilt_rocks_to_user(logged_user_id: int, 
                             rock:rockData_map,
                             db: Session = Depends(get_db)):
    return IltMeetingResponceService.assign_ilts_rocks(logged_user_id=logged_user_id,
                                                       user_id=rock.user_id, 
                                                       Ilt_id=rock.Ilt_id,
                                                       rock_id=rock.rock_id, 
                                                       db=db)
