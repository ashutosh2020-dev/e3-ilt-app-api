from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from app.schemas.meeting_response import MeetingResponse, checkIn, feedback, \
    TodoList, meetingReasponceRock, updatesData, IssueList
from app.exceptions.customException import CustomException


router = APIRouter()
IltMeetingResponceService = IltMeetingResponceService()


@router.get("/api/v1/ilts/meetingResponses/{meetingResponseId}")
def read_meeting_responce_details(meetingResponseId: int, UserId: int = Header(convert_underscores=False),  db: Session = Depends(get_db)):
    return IltMeetingResponceService.get_Ilts_meeting_list(user_id=UserId, meetingResponseId=meetingResponseId, db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/rocks")
def update_rocks_for_meetingResponse(meetingResponseId: int,
                                     rock: meetingReasponceRock, UserId: int = Header(convert_underscores=False),
                                     db: Session = Depends(get_db)):
    return IltMeetingResponceService.update_meetingResponce_rocks(user_id=UserId,
                                                                  meetingResponseId=meetingResponseId,
                                                                  name=rock.rockName,
                                                                  onTrack=rock.onTrack,
                                                                  db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/checkin")
def update_checkins_for_meetingResponse(meetingResponseId: int,
                                        checkIn: checkIn, UserId: int = Header(convert_underscores=False),
                                        db: Session = Depends(get_db)):
    return IltMeetingResponceService.update_meetingResponce_checkin(user_id=UserId,
                                                                    meetingResponseId=meetingResponseId,
                                                                    personalBest=checkIn.personalBest,
                                                                    professionalBest=checkIn.professionalBest,
                                                                    attendance=checkIn.attendance,
                                                                    db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/feedback")
def update_feedback_for_meetingResponse(meetingResponseId: int,
                                        feedback: feedback,
                                        UserId: int = Header(
                                            convert_underscores=False),
                                        db: Session = Depends(get_db)):
    return IltMeetingResponceService.update_meetingResponce_feedbacks(user_id=UserId,
                                                                      meetingResponseId=meetingResponseId,
                                                                      rating=feedback.rating,
                                                                      feedback=feedback.feedback,
                                                                      notes=feedback.notes,
                                                                      db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/todolist")
def create_update_ilt_meeting_todolist(meetingResponseId: int, toDoData: TodoList,
                                       UserId: int = Header(convert_underscores=False), db: Session = Depends(get_db)):
    try:
        for i in range(len(toDoData.todoItem)):
            responce = IltMeetingResponceService.create_update_to_do_list(user_id=UserId,
                                                                          id=toDoData.todoItem[i].todoListId,
                                                                          meetingResponseId=meetingResponseId,
                                                                          description=toDoData.todoItem[i].description,
                                                                          dueDate=toDoData.todoItem[i].dueDate,
                                                                          status=toDoData.todoItem[i].status,
                                                                          db=db)
        return responce
    except Exception as e:
        raise CustomException(
            500,  f"unable to process your request: {str(e)}")


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/updates")
def create_ilt_meeting_updates(meetingResponseId: int, ilt: updatesData,
                               UserId: int = Header(convert_underscores=False), db: Session = Depends(get_db)):

    for i in range(len(ilt.descriptions)):
        responce = IltMeetingResponceService.create_meeting_update(user_id=UserId,
                                                                   meetingResponseId=meetingResponseId,
                                                                   id=ilt.descriptions[i].updateId,
                                                                   description=ilt.descriptions[i].description,
                                                                   db=db)
    return responce


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/issues")
def create_update_ilt_meeting_issues(meetingResponseId: int,
                                     ilt: IssueList,
                                     UserId: int = Header(
                                     convert_underscores=False),
                                     db: Session = Depends(get_db)):
    for i in range(len(ilt.issues)):
        responce = IltMeetingResponceService.create_update_issue(user_id=UserId,
                                                                 meetingResponseId=meetingResponseId,
                                                                 id=ilt.issues[i].issueId,
                                                                 issue=ilt.issues[i].issue,
                                                                 priority=ilt.issues[i].priorityId,
                                                                 due_date=ilt.issues[i].date,
                                                                 resolves_flag=ilt.issues[i].resolvedFlag,
                                                                 recognize_performance_flag=ilt.issues[
                                                                     i].recognizePerformanceFlag,
                                                                 teacher_support_flag=ilt.issues[i].teacherSupportFlag,
                                                                 leader_support_flag=ilt.issues[i].leaderSupportFlag,
                                                                 advance_equality_flag=ilt.issues[i].advanceEquityFlag,
                                                                 others_flag=ilt.issues[i].othersFlag,
                                                                 assign_to_user_id=ilt.issues[i].assignTo,
                                                                 db=db)

    return responce


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}")
async def update_meeting_response(ilt_data: MeetingResponse, db: Session = Depends(get_db)):
    return IltMeetingResponceService.update_ilt_meeting_responses(data=ilt_data, db=db)
