from sqlalchemy.orm import Session
from app.models import MdlMeeting_rocks, MdlIlt_ToDoTask, Mdl_updates, \
            MdlMeetingsResponse, MdlIltMeetingResponses, MdlRocks, Mdl_issue, MdlUsers, MdlIltissue, MdlMeetings
from app.schemas.meeting_response import MeetingResponse, Duedate
from datetime import datetime, timezone
from typing import Annotated, Union



class IltMeetingResponceService:
    def get_Ilts_meeting_list(self, user_id: int, meetingResponseId :int, db: Session):
        try:
            user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
            if user is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "User not found"
                    }
            MeetingsResponse = db.query(MdlMeetingsResponse).filter(MdlMeetingsResponse.id == meetingResponseId).one_or_none()
            if MeetingsResponse is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "MeetingsResponse record not found"
                    }
            ilt_meet_re = db.query(MdlIltMeetingResponses)\
                                    .filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId).first()
            ilt_meet_id = ilt_meet_re.meeting_id
            user_meetingResponse_record = db.query(MdlMeetingsResponse)\
                                    .filter(MdlMeetingsResponse.id==meetingResponseId).first()        
            user_record = db.query(MdlUsers).filter(MdlUsers.id==ilt_meet_re.meeting_user_id).one()
            
            members_Info_dict= {"id":user_record.id,
                                        "first name":user_record.fname, 
                                        "last name":user_record.lname,
                                        "attandance":user_meetingResponse_record.attendance_flag,
                                        "personalBest":user_meetingResponse_record.checkin_personal_best,
                                        "professionalBest":user_meetingResponse_record.checkin_professional_best,
                                        "rating":user_meetingResponse_record.rating,
                                        "feedback":user_meetingResponse_record.feedback,
                                        "notes":user_meetingResponse_record.notes
                                        }
            user_rock_record =  [{
                                "rockId": record.id,
                                "onTrack": record.on_track_flag
                                }  \
                        for record in db.query(MdlMeeting_rocks)\
                        .filter(MdlMeeting_rocks.ilt_meeting_response_id==meetingResponseId)\
                        .all()
                        ]  
            user_update_record=[ record.description 
                        for record in db.query(Mdl_updates)\
                    .filter(Mdl_updates.meeting_response_id==meetingResponseId)\
                    .all()]
            user_todolist_record= [  {
                                "description": record.description,
                                "dueDate": record.due_date,
                                "status": record.status
                                } for record in db.query(MdlIlt_ToDoTask)\
                        .filter(MdlIlt_ToDoTask.meeting_response_id==meetingResponseId).all()]
            issue_record =  db.query(MdlIltissue)\
                        .filter(MdlIltissue.meeting_response_id == meetingResponseId).all()
            if not issue_record:
                return  {
                            "iltMeetingResponseId": meetingResponseId,
                            "iltMeetingId": ilt_meet_id,
                            "member": members_Info_dict,
                            "rocks": user_rock_record,
                            "updates": [
                                
                            ],
                            "todoList": [
                                {
                                "description": "",
                                "dueDate": "",
                                "status": ""
                                }
                            ],
                            "issues": [
                                {
                                "issueid": "",
                                "issue": "",
                                "priorityId": "",
                                "date": "",
                                "resolvedFlag": "",
                                "recognizePerformanceFlag": "",
                                "teacherSupportFlag": "",
                                "leaderSupportFlag": "",
                                "advanceEqualityFlag": "",
                                "othersFlag": ""
                                }
                            ]
                        } 

            user_issues_record = [db.query(Mdl_issue)\
                        .filter(Mdl_issue.id == record.id).one_or_none() for record in issue_record]
            

            # print(user_todolist_record)
            return {
                            "iltMeetingResponseId": meetingResponseId,
                            "iltMeetingId": ilt_meet_id,
                            "member": members_Info_dict,
                            "rocks": user_rock_record,
                            "updates": [
                                user_update_record
                            ],
                            "todoList": [
                                [
                                {"description": i_dict["description"],
                                "dueDate": i_dict["dueDate"],
                                "status": i_dict["status"] } for i_dict in user_todolist_record
                                ]
                            ],
                            "issues": [
                                [{
                                "issueid": user_issues_single_record.id,
                                "issue": user_issues_single_record.issue,
                                "priorityId": user_issues_single_record.priority,
                                "date": user_issues_single_record.created_at,
                                "resolvedFlag": user_issues_single_record.resolves_flag,
                                "recognizePerformanceFlag": user_issues_single_record.recognize_performance_flag,
                                "teacherSupportFlag": user_issues_single_record.teacher_support_flag,
                                "leaderSupportFlag": user_issues_single_record.leader_support_flag,
                                "advanceEqualityFlag": user_issues_single_record.advance_equality_flag,
                                "othersFlag": user_issues_single_record.others_flag
                                } for user_issues_single_record in user_issues_record]
                            ]
                        } 
        except Exception as e:
            return {
                    "confirmMessageID": "string",
                    "statusCode": 500,
                    "userMessage": f"unable to process your request: {e} "
                    }
    
    def create_meeting_responses_empty_for_ILTmember(self, meeting_id:int, member_list:list,db:Session):
        try:
            
            for uid in member_list:
                db_metting_response = MdlMeetingsResponse(attendance_flag = None , 
                                checkin_personal_best=None, checkin_professional_best=None,
                                rating = None, feedback=None, notes=None)
                db.add(db_metting_response)
                db.commit()
                db.refresh(db_metting_response)
                map_record = MdlIltMeetingResponses(meeting_id= meeting_id,
                                                     meeting_response_id = db_metting_response.id, meeting_user_id = uid)
                db.add(map_record)
                db.commit()
                db.refresh(map_record)
            return (True, "")
        except Exception as e:
            return (False, str(e))

    def create_meeting_responses(self, meeting_id:int, is_attand:bool, checkin_personal_best:str, 
                                 checkin_professional_best:str, ratings:int, feedback:str, notes:str, db:Session):
        db_metting_response = MdlMeetingsResponse(attendance_flag = is_attand , 
                            checkin_personal_best=checkin_personal_best, checkin_professional_best=checkin_professional_best,
                            rating = ratings, feedback=feedback, notes=notes)
        db.add(db_metting_response)
        db.commit()
        db.refresh(db_metting_response)
        map_record = MdlIltMeetingResponses(meeting_id= meeting_id, meeting_response_id = db_metting_response.id)
        db.add(map_record)
        db.commit()
        db.refresh(map_record)
        return True
    
    def create_ilts_rocks_meeting(self, user_id:int, name: str, description:str,meetingResponseId:int, onTrack:bool, db: Session):
        try:
            # check meetingResponseId
            user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
            if user is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "User_id not found"
                    }
            MeetingsResponse = db.query(MdlMeetingsResponse).filter(MdlMeetingsResponse.id == meetingResponseId).one_or_none()
            if MeetingsResponse is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "MeetingsResponse record not found"
                    }
            # db_rock = MdlRocks(name =name, description=description, on_track_flag=onTrack)
            db_rock = MdlRocks(name =name, description=description)
            db.add(db_rock)
            db.commit()
            db.refresh(db_rock)
            db_meeting_rocks = MdlMeeting_rocks(ilt_meeting_response_id = meetingResponseId, 
                                                    rock_id=db_rock.id, on_track_flag=onTrack)
            db.add(db_meeting_rocks)
            db.commit()
            db.refresh(db_meeting_rocks)
            return {
                    "confirmMessageID": "string",
                    "statusCode": 200,
                    "userMessage": "rock have successfully created and added to member's dashboard"
                }
        except Exception as e:
            return {
                    "confirmMessageID": "string",
                    "statusCode": 500,
                    "userMessage": f"unable to create rock: {str(e)}"
                }

    def create_ilts_meeting_rocks(self, user_id: int, meetingResponseId:int, rockId:int, 
                       onTrack:bool, db: Session):
        try:
            # check meetingResponseId, rockId
            # check if user_id is inside MdlIltMembers
            user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
            if user is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "User not found"
                    }
            MeetingsResponse = db.query(MdlMeetingsResponse).filter(MdlMeetingsResponse.id == meetingResponseId).one_or_none()
            if MeetingsResponse is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "MeetingsResponse record not found"
                    }
            check_rock_re = db.query(MdlRocks).filter(MdlRocks.id == rockId).one_or_none()
            if check_rock_re is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "please enter correct rock id"
                    }

            db_meeting_rocks = MdlMeeting_rocks(ilt_meeting_response_id = meetingResponseId, 
                                                rock_id=rockId, on_track_flag=onTrack)
            db.add(db_meeting_rocks)
            db.commit()
            db.refresh(db_meeting_rocks)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "rock added to the corresponding meetingRosponse id successfully"
                }
        except Exception as e:
            return {
                "confirmMessageID": "string",
                "statusCode": 0,
                "userMessage": f"unable to process your request {e}"
                }

    def create_to_do_list(self, user_id:int, meetingResponseId: int, description:str, 
                          dueDate:Duedate, status:bool, db:Session):
        try:
            # check if user_id is inside MdlIltMembers
            db_meeting_rocks = MdlIlt_ToDoTask(meeting_response_id = meetingResponseId, 
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
                "userMessage": f"unable to process your request: {str(e)} "
                }
    
    def create_meeting_update(self, user_id:int, meetingResponseId: int, description:str, db:Session):
        try:
            # checking if user_id is inside MdlUsers
            user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
            if user is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "User not found"
                    }
            db_meeting_update = Mdl_updates(meeting_response_id = meetingResponseId, 
                                                description=description)
            db.add(db_meeting_update)
            db.commit()
            db.refresh(db_meeting_update)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "updates has beem submited successfully"
                }
        except Exception as e:
            return {
                "confirmMessageID": "string",
                "statusCode": 0,
                "userMessage": "unable to process your request {str(e)}"
                }
    
    def create_issue(self, user_id:int, meetingResponseId: int, issue:str, priority:bool, 
                     created_at,
                     resolves_flag:bool,
                     recognize_performance_flag:bool,
                     teacher_support_flag:bool,
                     leader_support_flag:bool,
                     advance_equality_flag:bool,
                     others_flag:bool,
                     db:Session):

        try:
            # check if user_id is inside MdlIltMembers
            user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
            if user is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "User not found"
                    }
            responce_id = db.query(MdlMeetingsResponse).filter(MdlMeetingsResponse.id == meetingResponseId).one_or_none()
            if responce_id is None:
                return {
                    "confirmMessageID": "string",
                    "statusCode": 404,
                    "userMessage": "responce_id not found"
                    }
            db_issue = Mdl_issue(issue=issue,
                                        priority=priority,
                                        created_at=created_at,
                                        resolves_flag = resolves_flag,
                                        recognize_performance_flag= recognize_performance_flag,
                                        teacher_support_flag = teacher_support_flag,
                                        leader_support_flag =leader_support_flag,
                                        advance_equality_flag =advance_equality_flag,
                                        others_flag=others_flag
                                        )
            db.add(db_issue)
            db.commit()
            db.refresh(db_issue)
            db_meeting_issue = MdlIltissue(meeting_response_id = meetingResponseId, issue_id=db_issue.id)
            db.add(db_meeting_issue)
            db.commit()
            db.refresh(db_meeting_issue)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "issue have been created successfully"
                }
        except Exception as e:
            return {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"unable to process your request {str(e)}"
                }

    def update_ilt_meeting_responses(self, data:MeetingResponse, db: Session
                                    ):
        """
            these are the keys inside data
                iltMeetingResponseId: int 
                iltMeetingId ==> 
                member: members ==>
                attendance: bool,
                personalBest: str,
                professionalBest: str
                rating: int
                feedback: str
                notes: str
                rocks: List[Rock]
                updates: List[str]
                todoList: List[TodoItem]
                issues: List[Issue],
        """
        try:
            try:
                meetingResponse = db.query(MdlMeetingsResponse).filter(MdlMeetingsResponse.id == data.iltMeetingResponseId).one_or_none()
                if meetingResponse is None:
                    return {
                        "confirmMessageID": "string",
                        "statusCode": 404,
                        "userMessage": "MeetingsResponse record not found"
                        }
                
                # check does meeting is stated error msg - Meeting has started - Can not edit
                # meeting_id = db.query(MdlIltMeetingResponses).filter(MdlIltMeetingResponses.meeting_response_id == data.iltMeetingResponseId).first().meeting_id
                ilt_meeting_record= db.query(MdlMeetings).filter(MdlMeetings.id ==  data.iltMeetingId).one_or_none()
                
                ilt_meeting_start_time = ilt_meeting_record.schedule_start_at
                # print("testing meeting start is str or not",ilt_meeting_start_time)
                # print(type(ilt_meeting_start_time))
                given_time =  ilt_meeting_start_time.replace(tzinfo=timezone.utc) #datetime.strptime(ilt_meeting_start_time, '%Y-%m-%d %H:%M:%S.%f')
                current_time = datetime.now(timezone.utc)

                if current_time >= given_time and  current_time <= given_time:
                    return  {
                        "confirmMessageID": "string",
                        "statusCode": 404,
                        "userMessage": "meeting has started, unable to process your requests"
                        }
                # print("meeting will start at", given_time, "current time is", current_time)
                meetingResponseId = meetingResponse.id
                ilt_meetingResponce_map_record = db.query(MdlIltMeetingResponses)\
                                        .filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId).one()
                user_id, meeting_id = ilt_meetingResponce_map_record.meeting_user_id, ilt_meetingResponce_map_record.meeting_id  
                user_meetingResponse_record = db.query(MdlMeetingsResponse)\
                                        .filter(MdlMeetingsResponse.id==meetingResponseId).one()        
                user_record = db.query(MdlUsers).filter(MdlUsers.id==user_id).one()
                user_rock = db.query(MdlMeeting_rocks).filter(MdlMeeting_rocks.ilt_meeting_response_id==meetingResponseId).one()
                user_update_record=db.query(Mdl_updates).filter(Mdl_updates.meeting_response_id==meetingResponseId).one()
                issue_id=db.query(MdlIltissue).filter(MdlIltissue.meeting_response_id==meetingResponseId).one().issue_id
                user_issue_record= db.query(Mdl_issue).filter(Mdl_issue.id==issue_id).one()
                user_todo_record= db.query(MdlIlt_ToDoTask).filter(MdlIlt_ToDoTask.meeting_response_id==meetingResponseId).one()

            except Exception as e:
                return {
                        "confirmMessageID": "string",
                        "statusCode": 404,
                        "userMessage": f"all details with corresponding meeting responceId is not found, {str(e)}"
                        }
            user_record.fname=data.member.firstName
            user_record.lname= data.member.lastName
            user_meetingResponse_record.attendance_flag = data.attendance
            user_meetingResponse_record.checkin_personal_best = data.personalBest
            user_meetingResponse_record.checkin_professional_best = data.professionalBest
            user_meetingResponse_record.rating = data.rating
            user_meetingResponse_record.notes = data.notes

            user_rock.on_track_flag = data.rocks[0].onTrack

            user_update_record.description= data.updates[0]

            user_todo_record.description= data.todoList[0].description
            user_todo_record.due_date = data.todoList[0].dueDate
            user_todo_record.status = data.todoList[0].status
            user_issue_record.id = data.issues[0].issueid
            user_issue_record.issue = data.issues[0].issue
            user_issue_record.priority = data.issues[0].priority
            user_issue_record.created_at = data.issues[0].created_at
            user_issue_record.resolves_flag = data.issues[0].resolvedFlag
            user_issue_record.recognize_performance_flag = data.issues[0].recognizePerformanceFlag
            user_issue_record.teacher_support_flag = data.issues[0].teacherSupportFlag
            user_issue_record.leader_support_flag = data.issues[0].leaderSupportFlag
            user_issue_record.advance_equality_flag = data.issues[0].advanceEqualityFlag
            user_issue_record.others_flag = data.issues[0].othersFlag                   
            db.commit()                                                            
            db.refresh(user_record)
            db.refresh(user_meetingResponse_record)
            db.refresh(user_rock)
            db.refresh(user_update_record)
            db.refresh(user_todo_record)
            db.refresh(user_issue_record)
            return {
                        "confirmMessageID": "string",
                        "statusCode": 200,
                        "userMessage": "we have successfully all records"           
                    }
        except Exception as e:  
            return  {
                "confirmMessageID": "string",
                "statusCode": 500,
                "userMessage": f"Internal Server Error = {str(e)}"
                }