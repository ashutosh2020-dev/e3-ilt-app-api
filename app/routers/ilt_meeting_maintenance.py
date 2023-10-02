from fastapi import APIRouter, Depends, Body, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_meeting_service import IltMeetingService
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from app.schemas.ilt_meeting_schemas import MeetingData, rockData, rockData_map, Status, PendingData, whiteboardData
from datetime import datetime, timezone
from typing import Annotated, Union

router = APIRouter()
IltMeetingService = IltMeetingService()
IltMeetingResponceService = IltMeetingResponceService()


@router.get("/api/v1/ilts/{id}/meetings/scheduled")
def get_upcomming_Ilts_meeting_list(id: int, status:int=3, UserId: int = Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingService.get_upcomming_Ilts_meeting_list(user_id=UserId, statusId=status, ilt_id=id, db=db)

@router.get("/api/v1/ilts/{id}/meetings")
def get_ilt_meetings(id: int, UserId: int = Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingService.get_Ilts_meeting_list(user_id=UserId, ilt_id=id,  db=db)


@router.post("/api/v1/ilts/{id}/meetings")
def create_ilt_meeting(id: int, ilt: MeetingData, UserId: int = Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingService.create_ilts_meeting(ilt_id=id,
                                                 user_id=UserId,
                                                 scheduledStartDate=ilt.scheduledStartDate,
                                                 meetingStart=0,
                                                 meetingEnd=0,
                                                 location=ilt.location,
                                                 db=db)

@router.get("/api/v1/ilts/{id}/meetings/{meetingId}/meetingResponses")
def get_meeting_info_wrt_meeting_id_and_ilt_id(id: int, meetingId: int, UserId: int = Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingService.get_meeting_info(meeting_id=meetingId, iltId=id, User_id=UserId, db=db)


@router.post("/api/v1/ilts/{id}/meetings/{meetingId}")
def update_ilt_meeting(meetingId: int,
                       id: int,
                       iltMeeting: MeetingData,
                       UserId: int = Header(convert_underscores=False),
                       db: Session = Depends(get_db)):
    return IltMeetingService.update_ilt_meeting(meeting_id=meetingId,
                                                ilt_id=id,
                                                UserId=UserId,
                                                location=iltMeeting.location,
                                                scheduledStartDate=iltMeeting.scheduledStartDate,
                                                meetingStart=0,
                                                meetingEnd=0,
                                                db=db)


@router.post("/api/v1/ilts/{id}/meetings/{meetingId}/start")
def start_ilt_meeting(id: int, meetingId: int, UserId: int = Header(convert_underscores=False),
                      db: Session = Depends(get_db)):

    return IltMeetingService.start_ilt_meeting(meeting_id=meetingId,
                                               ilt_id=id,
                                               UserId=UserId,
                                               db=db)


@router.post("/api/v1/ilts/{id}/meetings/{meetingId}/stop")
def stop_ilt_meeting(id: int, meetingId: int, UserId: int = Header(convert_underscores=False),
                     db: Session = Depends(get_db)):

    return IltMeetingService.stop_ilt_meeting(meeting_id=meetingId,
                                              ilt_id=id,
                                              UserId=UserId,
                                              db=db)

@router.get("/api/v1/ilts/{id}/meetings/{meetingId}/pending")
def pending_ilt_meeting(id: int, meetingId: int, UserId: int = Header(convert_underscores=False),
                     db: Session = Depends(get_db)):

    return IltMeetingService.pending_issue_todo(meeting_id=meetingId,
                                              ilt_id=id,
                                              UserId=UserId,
                                              db=db)

@router.post("/api/v1/ilts/{id}/meetings/{meetingId}/transfer")
def transfer_ilt_meeting(id: int, meetingId: int,  pendingData:PendingData, UserId: int = Header(convert_underscores=False),
                     db: Session = Depends(get_db)):
    print(pendingData.listOfIssueIds)
    return IltMeetingService.transfer_ilt_meeting(meetingId=meetingId, listOfIssueIds=pendingData.listOfIssueIds, 
                                                  listOfToDoIds=pendingData.listOfToDoIds, 
                                                  futureMeetingId=pendingData.futureMeetingId, db=db)


@router.get("/api/v1/ilts/{id}/rocks")
def read_ilt_rocks(id: int, UserId: int = Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingResponceService.read_ilt_rock(user_id=UserId, ilt_id=id, db=db)


@router.post("/api/v1/ilts/meeting/create_rocks")
def create_ilt_rocks(rock: rockData, UserId: int = Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_ilts_rocks(user_id=UserId,
                                                       name=rock.name,
                                                       description=rock.description,
                                                       Ilt_id=rock.iltId,
                                                       db=db)


@router.post("/api/v1/ilts/meeting/assign_rocks")
def assign_ilt_rocks_to_user(rock: rockData_map,
                             UserId: int = Header(convert_underscores=False),
                             db: Session = Depends(get_db)):
    return IltMeetingResponceService.assign_ilts_rocks(logged_user_id=UserId,
                                                       user_ids=rock.userId,
                                                       Ilt_id=rock.iltId,
                                                       rock_id=rock.rockId,
                                                       rockOwnerId=rock.rockOwnerId,
                                                       db=db)

@router.post("/api/v1/ilts/meeting/update/whiteboard")
def create_ilt_rocks(whiteboard:whiteboardData, user_id:int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltMeetingService.update_ilts_whiteboard(user_id=user_id,
                                                    whiteboard=whiteboard,
                                                    db=db)