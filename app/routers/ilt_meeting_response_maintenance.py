from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from app.schemas.meeting_response import MeetingResponse, TodoList, Createdate, RockUpdate, updatesData, IssueList
from datetime import datetime
from typing import Annotated, Union


router = APIRouter()
IltMeetingResponceService = IltMeetingResponceService()
 

@router.get("/api/v1/ilts/meetingResponses/{meetingResponseId}")
def read_meeting_responce_details(user_id: int, meetingResponseId:int,  db: Session = Depends(get_db)):
    return IltMeetingResponceService.get_Ilts_meeting_list(user_id=user_id, meetingResponseId=meetingResponseId, db=db)


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/rocks")
def assign_ilt_rocks_to_meetingResponse(user_id: int, meetingResponseId:int, 
                                        rock:RockUpdate,
                                        db: Session = Depends(get_db)):
    return IltMeetingResponceService.create_ilts_meeting_rocks(user_id= user_id, 
                                                               meetingResponseId= meetingResponseId,
                                                               rockId= rock.rock_id, 
                                                               onTrack = rock.onTrack,
                                                               db = db)

@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/todolist")
def create_ilt_meeting_todolist(user_id:int, meetingResposnceId:int, toDoData:TodoList, 
                                db: Session = Depends(get_db)):
    try:
        for i in range(len(toDoData.TodoItem)):
            responce = IltMeetingResponceService.create_to_do_list(user_id=user_id, 
                                                        meetingResponseId=meetingResposnceId, 
                                                        description=toDoData.TodoItem[i].description,
                                                        dueDate=toDoData.TodoItem[i].duedate,
                                                        status=toDoData.TodoItem[i].status,
                                                        db=db)
            if responce['statusCode']!=200:
                return responce
            else:
                pass
        return {
                    "confirmMessageID": "string",
                    "statusCode": 200,
                    "userMessage": "all to-do list created successfully"
                    }
    except Exception as e:
        return {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"unable to process your request: {str(e)} "
                }



@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/updates")
def create_ilt_meeting_updates(user_id:int, meetingResponseId:int,ilt:updatesData, db: Session = Depends(get_db)):
     
    try:
        for i in range(len(ilt.descriptions)):
            responce = IltMeetingResponceService.create_meeting_update(user_id=user_id, 
                                                           meetingResponseId=meetingResponseId, 
                                                           description=ilt.descriptions[i].description, 
                                                           db=db)
            if responce['statusCode']!=200:
                return responce
            else:
                pass
        return {
                    "confirmMessageID": "string",
                    "statusCode": 200,
                    "userMessage": "all updates has inserted successfully"
                    }
    except Exception as e:
        return {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"unable to process your request: {str(e)} "
                }


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}/issues")
def create_ilt_meeting_issues(user_id:int, meetingResponseId: int,
                     ilt:IssueList,
                     db: Session = Depends(get_db)):
    try:
        for i in range(len(ilt.issues)):
            responce = IltMeetingResponceService.create_issue(user_id=user_id, 
                     meetingResponseId=meetingResponseId, 
                     issue=ilt.issues[i].issue, 
                     priority=ilt.issues[i].priorityId, 
                     created_at = ilt.issues[i].date,
                     resolves_flag=ilt.issues[i].resolvedFlag,
                     recognize_performance_flag=ilt.issues[i].recognizePerformanceFlag,
                     teacher_support_flag=ilt.issues[i].teacherSupportFlag,
                     leader_support_flag=ilt.issues[i].leaderSupportFlag,
                     advance_equality_flag=ilt.issues[i].advanceEqualityFlag,
                     others_flag=ilt.issues[i].othersFlag,
                     db=db)
            if responce['statusCode']!=200:
                return responce
            else:
                pass
        return {
                    "confirmMessageID": "string",
                    "statusCode": 200,
                    "userMessage": "all issues has created successfully"
                    }
    except Exception as e:
        return {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"unable to process your request: {str(e)}"
                }


@router.post("/api/v1/ilts/meetingResponses/{meetingResponseId}")
async def update_meeting_response(ilt_data: MeetingResponse, db: Session= Depends(get_db)):
    return IltMeetingResponceService.update_ilt_meeting_responses(data = ilt_data, db=db)
