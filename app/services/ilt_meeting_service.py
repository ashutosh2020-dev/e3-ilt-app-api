from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models import MdlIltMeetings, MdlMeetings, MdlUsers, MdlIlts, \
    MdlIltMembers, MdlIltMeetingResponses, MdlMeetingsResponse,  \
    Mdl_updates, MdlIlt_ToDoTask, MdlIltissue, Mdl_issue, MdlIltMeetingWhiteBoard, MdlIltWhiteBoard
import sys
from app.schemas.ilt_meeting_schemas import Status, whiteboardData, whiteboardDataInfo
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from datetime import datetime, timezone, timedelta
from app.exceptions.customException import CustomException


def calculate_meeting_status(schedule_start_at, start_at, end_at):
    current_datetime = datetime.now()
    if current_datetime < schedule_start_at and start_at == 0:
        return 0  # notStarted
    elif current_datetime > schedule_start_at and start_at==0:
        return 0 # skipped
    elif current_datetime >= start_at and end_at == 0:
        return 1  # inProgress
    else:
        return 2  # completed


class IltMeetingService:
    def get_upcomming_Ilts_meeting_list(self, user_id: int, statusId, ilt_id: int, db: Session):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
        if not user:
            raise CustomException(400,  "User not found")
        check_ilt = db.query(MdlIlts).filter(
            MdlIlts.id == ilt_id).one_or_none()
        if check_ilt is None:
            raise CustomException(400,  "Ilt not found")
        list_meeting_records = (db.query(MdlMeetings)
                                .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                .filter(MdlIltMeetings.ilt_id == ilt_id)
                                .order_by(MdlMeetings.schedule_start_at.asc())
                                .all()
                                )
        if list_meeting_records:
            ilt_list = []
            for meeting_record in list_meeting_records:
                schedule_start_at = meeting_record.schedule_start_at
                start_meeting_time = meeting_record.start_at if meeting_record.start_at else 0
                end_meeting_time = meeting_record.end_at if meeting_record.end_at else 0
                status = calculate_meeting_status(
                    schedule_start_at, start_meeting_time, end_meeting_time)
                if status == statusId or statusId==3 :
                    ilt_list.append({
                                    "iltId": ilt_id,
                                    "iltMeetingId": meeting_record.id,
                                    "scheduledStartDate":(meeting_record.schedule_start_at 
                                    if meeting_record.schedule_start_at else meeting_record.schedule_start_at),
                                    "meetingStart": (meeting_record.start_at
                                    if meeting_record.start_at else meeting_record.start_at),
                                    "meetingEnd": (meeting_record.end_at 
                                    if meeting_record.end_at else meeting_record.end_at),
                                    "location": meeting_record.location,
                                    "meetingStatus": status,
                                    "noteTakerId":meeting_record.note_taker_id
                                    })
            return ilt_list
        else:
            return []

    def get_Ilts_meeting_list(self, user_id: int, ilt_id: int, db: Session):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
        if not user:
            raise CustomException(400,  "User not found")
        check_ilt = db.query(MdlIlts).filter(
            MdlIlts.id == ilt_id).one_or_none()
        if check_ilt is None:
            raise CustomException(400,  "Ilt not found")
        list_meetings = [record.ilt_meeting_id
                         for record in db.query(MdlIltMeetings)
                         .filter(MdlIltMeetings.ilt_id == ilt_id)
                         .order_by(MdlIltMeetings.id.asc())
                         .all()]
        if list_meetings:
            ilt_list = []
            for mid in list_meetings:
                meeting_record = db.query(MdlMeetings).filter(
                    MdlMeetings.id == mid).one()
                schedule_start_at = meeting_record.schedule_start_at
                start_meeting_time = meeting_record.start_at if meeting_record.start_at else 0
                end_meeting_time = meeting_record.end_at if meeting_record.end_at else 0
                status = calculate_meeting_status(
                    schedule_start_at, start_meeting_time, end_meeting_time)
                note_taker_id = meeting_record.note_taker_id

                val = {
                    "iltId": ilt_id,
                    "ownerId":check_ilt.owner_id,
                    "noteTakerId":note_taker_id, 
                    "iltMeetingId": mid,
                    "scheduledStartDate": (meeting_record.schedule_start_at 
                                    if meeting_record.schedule_start_at else meeting_record.schedule_start_at),
                    "meetingStart": (meeting_record.start_at
                                    if meeting_record.start_at else meeting_record.start_at),
                    "meetingEnd": (meeting_record.end_at 
                                    if meeting_record.end_at else meeting_record.end_at),
                    "location": meeting_record.location,
                    "meetingStatus": status
                }
                ilt_list.append(val)

            return ilt_list
        else:
            return []
    def get_pending_issue_todo_ids(self, meeting_id, db:Session):
        ## check pending- issue, todo, 
        member_meeting_response_id_list = [map_record.meeting_response_id 
                                            for map_record in db.query(MdlIltMeetingResponses)
                                            .filter(MdlIltMeetingResponses.meeting_id==meeting_id)
                                            .all()]
        member_meeting_responce_records = [db.query(MdlMeetingsResponse)
                                                .filter(MdlMeetingsResponse.id==m_r_id).one() 
                                                for m_r_id in member_meeting_response_id_list]
        pending_issue_record_list = []
        pending_to_do_record_list = []
        for responceRecord in member_meeting_responce_records:
            meeting_response_id = responceRecord.id
            ##issue
            pending_issue_record_list = set([id for id, in db.query(Mdl_issue.id)
                                        .join(MdlIltissue, Mdl_issue.id==MdlIltissue.issue_id )
                                        .filter(and_(MdlIltissue.meeting_response_id==meeting_response_id, 
                                                     Mdl_issue.resolves_flag==False, 
                                                     Mdl_issue.priority !=4))
                                        .all()])
            ##ToDo
            pending_to_do_record_list = [p_todo_id for p_todo_id, in db.query(MdlIlt_ToDoTask.id)
                                        .filter(and_(MdlIlt_ToDoTask.meeting_response_id==meeting_response_id,
                                                     MdlIlt_ToDoTask.status == False))
                                        .all()]        
            return pending_issue_record_list, pending_to_do_record_list


    def create_ilts_meeting(self, ilt_id: int, user_id: int,  scheduledStartDate,
                             noteTakerId, db: Session, pastData_flag:bool, location: str):

        user_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if user_record is None:
            raise CustomException(404,  "User not found")
        Ilt_record = db.query(MdlIlts).filter(
            MdlIlts.id == ilt_id).one_or_none()
        if Ilt_record is None:
            raise CustomException(404,  "ILT not found")

        current_date = datetime(2020, 1, 1, 00, 00)
        if scheduledStartDate < current_date and pastData_flag == False:
            raise CustomException(
                404, "Please enter correct date, Date must be greater than currect date")
        db_meeting = MdlMeetings()
        db_meeting.schedule_start_at = scheduledStartDate
        if location:
            db_meeting.location = location
        if noteTakerId:
            db_meeting.note_taker_id = noteTakerId

        db.add(db_meeting)
        db.commit()
        db.refresh(db_meeting)
        ilt_members_list = [record.member_id for record in db.query(MdlIltMembers)
                            .filter(MdlIltMembers.ilt_id == ilt_id).all()]
        # create meeting response and update the map table(MdlIltMeetingResponses) for  meeting id and m_response_id
        status, msg = (IltMeetingResponceService()
                       .create_meeting_responses_empty_for_ILTmember(meeting_id=db_meeting.id,
                                                                     member_list=ilt_members_list, iltId=ilt_id, db=db))
        if status is not True:
            raise CustomException(
                404,  f"Unable to create meeting responce : {msg}")

        # update map table about new ilt and ilt_meeting's relationship
        db_ilt_meeting = MdlIltMeetings(
            ilt_id=ilt_id, ilt_meeting_id=db_meeting.id )
        db.add(db_ilt_meeting)
        db.commit()
        db.refresh(db_ilt_meeting)
        
        # pull all pending issue from the last end meeting 
        latest_meeting_re = (db.query(MdlMeetings)
             .join(MdlIltMeetings, MdlIltMeetings.ilt_id==MdlMeetings.id)
                .filter(MdlIltMeetings.ilt_id==ilt_id)
                .order_by(MdlMeetings.schedule_start_at.desc())
                .first())
        msg = "."
        if latest_meeting_re:
            if latest_meeting_re.end_at is not None:
                pending_issue_record_list, \
                pending_to_do_record_list = self.get_pending_issue_todo_ids(meeting_id=latest_meeting_re.id,
                                                                            db=db)
            
                _success = self.transfer_ilt_meeting(meetingId=latest_meeting_re.id,ilt_id=ilt_id,
                                        UserId=user_id,
                                        listOfIssueIds= pending_issue_record_list, 
                                        listOfToDoIds = pending_to_do_record_list, 
                                        futureMeetingId= db_meeting.id, 
                                        check_end_meeting_flag= False,
                                        db=db)
                msg = "with all Pending items from the last meeting." 
            else:
                pass
                         

        return {
            "statusCode": 200,
            "userMessage": f"meeting has been created{msg}"
        }

    def update_ilt_meeting(self, UserId: int, meeting_id: int, ilt_id: int, location, scheduledStartDate, noteTakerId,  db: Session):
        if db.query(MdlUsers).filter(MdlUsers.id == UserId).one_or_none() is None:
            raise CustomException(404,  "userId did not found ")
        check_ilt_meeting_record = (db.query(MdlIltMeetings)
                                    .filter(MdlIltMeetings.ilt_id == ilt_id,
                                    MdlIltMeetings.ilt_meeting_id == meeting_id)
                                    .one_or_none())
        if check_ilt_meeting_record is None:
            raise CustomException(
                404,  "Meeting ID is not associated with ILT id")
        if scheduledStartDate:
            if scheduledStartDate < datetime(2020, 1, 1, 00, 00):
                raise CustomException(
                    400,  "Please enter correct date, dates must be greater than currect data")

        db_meeting = db.query(MdlMeetings).filter(
            MdlMeetings.id == meeting_id).one_or_none()
        if db_meeting is None:
            raise CustomException(404,  "meeting records not found")
        if db_meeting.end_at:
            raise CustomException(404,  "Meeting has been ended, Can not update it")
        if location:
            db_meeting.location = location
        if scheduledStartDate:
            db_meeting.schedule_start_at = scheduledStartDate
        if noteTakerId:
            db_meeting.note_taker_id = noteTakerId
        db.commit()
        return {
            "statusCode": 200,
            "userMessage": "meeting have successfully updated"
        }
        

    def get_meeting_info(self, User_id: int, iltId: int, meeting_id: int,  db: Session):
        try: 
            user = db.query(MdlUsers).filter(
                MdlUsers.id == User_id).one_or_none()
            if user is None:
                raise CustomException(404,  "User_id not found")
            ilt_record = db.query(MdlIlts).filter(
                MdlIlts.id == iltId).one_or_none()
            if ilt_record is None:
                raise CustomException(404,  "ilt_id not found")
            ilt_meeting_record = db.query(MdlMeetings).filter(
                MdlMeetings.id == meeting_id).one_or_none()
            if ilt_meeting_record is None:
                raise CustomException(404,  "ilt_meeting records not found")
            db_ilt_meeting_record = (db.query(MdlIltMeetings)
                                     .filter(and_(MdlIltMeetings.ilt_id == iltId,
                                             MdlIltMeetings.ilt_meeting_id == meeting_id))
                                     .one_or_none())
            if db_ilt_meeting_record is None:
                raise CustomException(
                    404,  "Meeting ID is not associated with ILT id")
            ilt_members_ids = []
            current_ilt_members_ids = [id for id, in db.query(MdlIltMembers.member_id)
                                       .filter(MdlIltMembers.ilt_id==iltId)
                                       .all()]             
            if (User_id in current_ilt_members_ids) or (user.role_id == 4):
                user_ids = [userId for userId, in db.query(MdlIltMeetingResponses.meeting_user_id)\
                    .filter(MdlIltMeetingResponses.meeting_id == meeting_id).all()]
                ilt_members_ids.extend(user_ids)
            else:
                raise CustomException( 404,  "Invalid user")

            members_Info_dict = []
            meeting_response_id = 0
            noteTakerId = ilt_meeting_record.note_taker_id
            
            for uid in ilt_members_ids:
                user_record = db.query(MdlUsers).filter(
                    MdlUsers.id == uid).one()
                meeting_response_row = (db.query(MdlIltMeetingResponses)
                    .filter(and_(MdlIltMeetingResponses.meeting_id == meeting_id,
                            MdlIltMeetingResponses.meeting_user_id == uid)).one_or_none())
                if meeting_response_row is None:
                    continue
                
                meeting_response_id = meeting_response_row.meeting_response_id
                meeting_response_record = db.query(MdlMeetingsResponse)\
                    .filter(MdlMeetingsResponse.id == meeting_response_id).one()
        
                update_records = db.query(Mdl_updates)\
                    .filter(Mdl_updates.meeting_response_id == meeting_response_id)\
                    .all()
                user_update_record = [
                    {
                        "updateId": record.id,
                        "description": record.description
                    }
                    for record in update_records
                ] if update_records else []
                todo_task_records = db.query(MdlIlt_ToDoTask)\
                    .filter(MdlIlt_ToDoTask.meeting_response_id == meeting_response_id)\
                    .all()
                user_todolist_record = [
                    {
                        "todoListId": record.id,
                        "description": record.description,
                        "dueDate": record.due_date,
                        "status": record.status
                    }
                    for record in todo_task_records
                ] if todo_task_records else []

                issue_record = db.query(MdlIltissue)\
                    .filter(MdlIltissue.meeting_response_id == meeting_response_id).order_by(MdlIltissue.id.desc()).all()

                user_issues_record = [db.query(Mdl_issue)
                                      .filter(Mdl_issue.id == record.issue_id).one_or_none() for record in issue_record]  \
                    if issue_record else []
                # print("---",meeting_response_id, [(user_issues_single_record.created_at,
                #                                    user_issues_single_record.issue_resolve_date,
                #                                    user_issues_single_record.resolves_flag,
                #                                     user_issues_single_record.due_date - datetime.utcnow()) 
                #                                   for user_issues_single_record in user_issues_record])
                members_Info_dict.append(
                    {
                        "iltMeetingResponseId": meeting_response_id,
                        "iltMeetingId": meeting_id,
                        "noteTakerId":noteTakerId,
                        "member": {
                            "userId": user_record.id,
                            "firstName": user_record.fname,
                            "lastName": user_record.lname,
                            "emailId": user_record.email
                        },
                        "attendance": meeting_response_record.attendance_flag,
                        "personalBest": meeting_response_record.checkin_personal_best,
                        "professionalBest": meeting_response_record.checkin_professional_best,
                        "rating": meeting_response_record.rating,
                        "feedback": meeting_response_record.feedback,
                        "notes": meeting_response_record.notes,
                        "rockName": meeting_response_record.rockName,
                        "onTrack": meeting_response_record.onTrack,
                        "updates": user_update_record,
                        "todoList": user_todolist_record,
                        "issues":
                        [{
                            "issueId": user_issues_single_record.id,
                            "issue": user_issues_single_record.issue,
                            "priorityId": user_issues_single_record.priority,
                            "date": user_issues_single_record.due_date,
                            "resolvedFlag": user_issues_single_record.resolves_flag,
                            "recognizePerformanceFlag": user_issues_single_record.recognize_performance_flag,
                            "teacherSupportFlag": user_issues_single_record.teacher_support_flag,
                            "leaderSupportFlag": user_issues_single_record.leader_support_flag,
                            "advanceEquityFlag": user_issues_single_record.advance_equality_flag,
                            "othersFlag": user_issues_single_record.others_flag,
                            "numberOfdaysIssueDelay":  (user_issues_single_record.issue_resolve_date - user_issues_single_record.created_at).days
                                                        if (user_issues_single_record.resolves_flag == True and user_issues_single_record.issue_resolve_date)
                                                        else  (user_issues_single_record.due_date - datetime.utcnow()).days, 
                            "isRepeated": (True if db.query(MdlIltissue)
                                                    .filter(MdlIltissue.issue_id==user_issues_single_record.id).count()>1 
                                                else False)
                        } for user_issues_single_record in user_issues_record]
                        if user_issues_record else []
                    }
                )
            return members_Info_dict
        except Exception as e:
            raise CustomException(500,  f"Internal server error {str(e)}")

    def start_ilt_meeting(self, UserId: int, pastData_flag:bool, meeting_id: int, ilt_id: int, db: Session):

        if db.query(MdlUsers).filter(MdlUsers.id == UserId).one_or_none() is None:
            raise CustomException(400,  "User did not found ")
        if db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none() is None:
            raise CustomException(400,  "Ilt did not found ")
    
        ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==ilt_id).one_or_none()
        db_meeting = db.query(MdlMeetings).filter(MdlMeetings.id == meeting_id).one_or_none()
        
        if UserId not in [ownerId, db_meeting.note_taker_id]:
            raise CustomException(404,  "Only Ilt Owner or Note Taker can start the meeting.")
        
        difference = (db_meeting.schedule_start_at - datetime.utcnow()).total_seconds()
        diff = difference/60 
        if diff > 2 and pastData_flag == False:
            raise CustomException(400,  "Meeting can start only after meeting schedule time. Please adjust the meeting schedule(Use UTC format only).")
        if db_meeting is None:
            raise CustomException(404,  "Meeting records not found")
        
        db_meeting.start_at = datetime.utcnow() if pastData_flag==False else db_meeting.schedule_start_at
        db.commit()
        db.refresh(db_meeting)
        db.close()
        return {
            "confirmMessageID": "string",
            "statusCode": 200,
            "userMessage": "Meeting have started successfully"
        }
        
    def stop_ilt_meeting(self, UserId: int, meeting_id: int, ilt_id: int,pastData_flag:bool, db: Session):
        if db.query(MdlUsers).filter(MdlUsers.id == UserId).one_or_none() is None:
            raise CustomException(400,  "No users available ")
        if db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none() is None:
            raise CustomException(400,  "No Ilt present")
        
        ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==ilt_id).one_or_none()
        db_meeting = db.query(MdlMeetings).filter(
            MdlMeetings.id == meeting_id).one_or_none()
        if db_meeting is None:
            raise CustomException(400,  "Meeting records is not available")
        
        if UserId != db_meeting.note_taker_id and UserId != ownerId:
            raise CustomException(404,  "Only Ilt owner and Note Taker can edit the data.")
        
        if db_meeting.start_at is None:
            raise CustomException(400,  "Meeting has not started")
        
        if db_meeting.start_at:
            db_meeting.end_at = datetime.utcnow() if pastData_flag == False else db_meeting.schedule_start_at + timedelta(hours=1)
            db.commit()
            db.refresh(db_meeting)
        # taking White Board snapshot for meeting(common View across all meeting)
        currect_des_of_whiteboard, = db.query(MdlIltWhiteBoard.description).filter(MdlIltWhiteBoard.iltId==ilt_id).one_or_none()
        db_whiteB = MdlIltMeetingWhiteBoard(description=currect_des_of_whiteboard, meetingId=meeting_id)
        db.add(db_whiteB)
        db.commit()
        db.refresh(db_whiteB)

        return {
            "confirmMessageID": "string",
            "statusCode": 200,
            "userMessage": "Meeting have successfully ended",
        }

    def pending_issue_todo_raw(self, meeting_id ,db):
            num_of_attand_members = 0
            num_of_feedback_in_attand_members = 0
            ## check pending- issue, todo, 
            member_meeting_response_id_list = [map_record.meeting_response_id 
                                                for map_record in db.query(MdlIltMeetingResponses)
                                                .filter(MdlIltMeetingResponses.meeting_id==meeting_id)
                                                .all()
                                                ]
            member_meeting_responce_records = [db.query(MdlMeetingsResponse)
                                                    .filter(MdlMeetingsResponse.id==m_r_id).one() 
                                                    for m_r_id in member_meeting_response_id_list]
            pending_issue_record_list = []
            pending_to_do_record_list = []
            for responceRecord in member_meeting_responce_records:
                meeting_response_id = responceRecord.id
                num_of_attand_members += 1 if responceRecord.attendance_flag else 0
                num_of_feedback_in_attand_members += 1 if responceRecord.rating and responceRecord.attendance_flag else 0
                ##issue
                list_of_issue_records = (db.query(MdlIltissue)
                                            .filter(MdlIltissue.meeting_response_id==meeting_response_id)
                                            .all())
                                                    
                issue_id_list = [record.issue_id for record in list_of_issue_records] if  list_of_issue_records else []
                
                if issue_id_list:
                    for issue_id in issue_id_list:
                            issue_record = db.query(Mdl_issue).get(issue_id)
                            if issue_record.resolves_flag == False and issue_record.priority !=4:
                                pending_issue_record_list.append({
                                    "issueId": issue_record.id,
                                    "issue": issue_record.issue,
                                    "priorityId": issue_record.priority,
                                    "date": issue_record.created_at,
                                    "resolvedFlag": issue_record.resolves_flag,
                                    "recognizePerformanceFlag": issue_record.recognize_performance_flag,
                                    "teacherSupportFlag": issue_record.teacher_support_flag,
                                    "leaderSupportFlag": issue_record.leader_support_flag,
                                    "advanceEquityFlag": issue_record.advance_equality_flag,
                                    "othersFlag": issue_record.others_flag
                                })

                ##ToDo
                list_of_toDo_records = (db.query(MdlIlt_ToDoTask)
                                            .filter(MdlIlt_ToDoTask.meeting_response_id==meeting_response_id)
                                            .all())
                if list_of_toDo_records:
                    for todo_record in list_of_toDo_records:
                            if todo_record.status == False:
                                pending_to_do_record_list.append({
                                    "todoListId": todo_record.id,
                                    "description": todo_record.description,
                                    "dueDate": todo_record.due_date,
                                    "status": todo_record.status
                                })
            return (num_of_attand_members,num_of_feedback_in_attand_members, pending_issue_record_list,
                     pending_to_do_record_list, len(member_meeting_responce_records))
        
    def pending_issue_todo(self, UserId: int, meeting_id: int, ilt_id: int, db: Session):
        if db.query(MdlUsers).filter(MdlUsers.id == UserId).one_or_none() is None:
            raise CustomException(400,  "No users available ")
        if db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none() is None:
            raise CustomException(400,  "No Ilt present")

        meeting_re = db.query(MdlMeetings).filter(
            MdlMeetings.id == meeting_id).one_or_none()
        if meeting_re is None:
            raise CustomException(400,  "Meeting records is not available")
        
        num_of_attand_members,\
        num_of_feedback_in_attand_members,\
        pending_issue_record_list,\
        pending_to_do_record_list, num_of_member = self.pending_issue_todo_raw(meeting_id, db)
        future_meetings_list = self.get_upcomming_Ilts_meeting_list(user_id=UserId, 
                                                                    statusId=0, 
                                                                    ilt_id=ilt_id, db=db)  # (here 0 is for meeting which are notStarted )
        attandancePercentage = (num_of_attand_members / num_of_member) * 100
        attandiesFeedbackPercentage = (num_of_feedback_in_attand_members/num_of_attand_members)*100 if num_of_attand_members != 0 else 0

        return {
                "iltId": ilt_id,
                "meetingId":meeting_id,
                "attandancePercentage":attandancePercentage,
                "attandiesFeedbackPercentage":attandiesFeedbackPercentage,
                "issues":pending_issue_record_list,
                "todoList":pending_to_do_record_list,
                "futureMeetings":future_meetings_list
            }


    def transfer_ilt_meeting(self, meetingId:int,ilt_id:int, UserId:int, listOfIssueIds:list, listOfToDoIds:list, futureMeetingId:int, db:Session, check_end_meeting_flag=True):
        """
        as input
        {
            listOfIssueIds:[],
            listOfToDoIds:[],
            futureMeetingId:int
        }
        extract parent userId
        extract meetingResID 
        update both issueMap and todo table
        """
        
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meetingId).one_or_none()
        if meeting_re.start_at is None:
            raise CustomException(404,  "Please Start the meeting first")
        if meeting_re.end_at and check_end_meeting_flag :
            raise CustomException(404,  "We can only transfer meeting's pendings when meeting is in-progress.")
        
        ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==ilt_id).one_or_none()
        if UserId != meeting_re.note_taker_id and UserId != ownerId:
            raise CustomException(404,  "Only Ilt owner and Note Taker can transfer meeting's pendings.")
            
        # transfering pending ilt
        for id in listOfIssueIds:
            map_re = (db.query(MdlIltissue).filter(MdlIltissue.issue_id==id)
                    .order_by(MdlIltissue.id.desc()).first())
            

            # = map_re.parent_meeting_responce_id 
            parent_responce_id= map_re.meeting_response_id 
            parent_user_id = (db.query(MdlIltMeetingResponses)
                            .filter(MdlIltMeetingResponses.meeting_response_id==parent_responce_id).first().meeting_user_id
                            )
            current_meetingResponce= (db.query(MdlIltMeetingResponses)
                            .filter(MdlIltMeetingResponses.meeting_user_id==parent_user_id,
                                    MdlIltMeetingResponses.meeting_id==futureMeetingId).first().meeting_response_id)
            
            check_issue_record = (db.query(MdlIltissue)
                            .filter(MdlIltissue.meeting_response_id==current_meetingResponce,
                                    MdlIltissue.issue_id==id).one_or_none())
            
            if check_issue_record is not None:
                continue
            # create re with MdlIltissue
            db_issue_map = MdlIltissue(
                meeting_response_id= current_meetingResponce,
                issue_id = id, 
                parent_meeting_responce_id= parent_responce_id)
            db.add(db_issue_map)
            db.commit()
            db.refresh(db_issue_map)

        # transfering pending todo
        for id in listOfToDoIds:
            parent_todo_record = (db.query(MdlIlt_ToDoTask)
                            .filter(MdlIlt_ToDoTask.id==id).order_by(MdlIlt_ToDoTask.id.desc()).first()
                            )
            if parent_todo_record is None:
                raise CustomException(400,  "records is not available")
            parent_user_id = (db.query(MdlIltMeetingResponses)
                            .filter(MdlIltMeetingResponses.meeting_response_id==parent_todo_record.meeting_response_id).first().meeting_user_id
                            )
            current_meetingResponce= (db.query(MdlIltMeetingResponses)
                            .filter(MdlIltMeetingResponses.meeting_user_id==parent_user_id,
                                    MdlIltMeetingResponses.meeting_id==futureMeetingId).first().meeting_response_id)    
            check_todo_record = (db.query(MdlIlt_ToDoTask)
                            .filter(MdlIlt_ToDoTask.meeting_response_id==current_meetingResponce,
                                    MdlIlt_ToDoTask.parent_to_do_id==parent_todo_record.id).all())
            print("--")
            if check_todo_record:
                continue
            
            # create re with MdlIlt_ToDoTask 
            db_todo_record = MdlIlt_ToDoTask(
                                meeting_response_id=current_meetingResponce, 
                                description=parent_todo_record.description, 
                                due_date=parent_todo_record.due_date, 
                                created_at= datetime.utcnow(),
                                status=parent_todo_record.status, 
                                parent_to_do_id=parent_todo_record.id)                               
            db.add(db_todo_record)
            db.commit()
            db.refresh(db_todo_record)
            
    
        return {
                "statusCode": 200,
                "userMessage": "meeting have successfully updated"
            }

    def ilts_whiteboard_info(self, user_id: int, whiteboard:whiteboardDataInfo, db:Session):
        
        check_ilt_id = db.query(MdlIlts).filter(MdlIlts.id == whiteboard.iltId).one_or_none()
        if check_ilt_id is None:
            raise CustomException(404,  "Ilt not found")  
        check_meeting_re = db.query(MdlIltMeetings).filter(and_(MdlIltMeetings.ilt_id==whiteboard.iltId,
                                         MdlIltMeetings.ilt_meeting_id==whiteboard.meetingId)).one_or_none()
        if check_meeting_re is None:
            raise CustomException(404,  "This meeting is not associated with current Ilt")
        
        check_meeting_end_date, = db.query(MdlMeetings.end_at).filter(MdlMeetings.id==whiteboard.meetingId).one()
        
        whiteboardDataInfoObj = whiteboardDataInfo()
        whiteB_re = db.query(MdlIltWhiteBoard).filter(MdlIltWhiteBoard.iltId == whiteboard.iltId).one_or_none()
        if whiteB_re is None:
            raise CustomException(404,  "WhiteBoard is not available for this ILT")
        
        
        if check_meeting_end_date is not None:
            # if meeting is end- show snap of responces
            whiteB_meeting_re = (db.query(MdlIltMeetingWhiteBoard)
                                    .filter(MdlIltMeetingWhiteBoard.meetingId == whiteboard.meetingId)
                                    .one_or_none())
            if whiteB_meeting_re is None:
                raise CustomException(404,  "no whiteboard is available for this meeting") 
            whiteboardDataInfoObj.iltId= whiteboard.iltId
            whiteboardDataInfoObj.description= whiteB_meeting_re.description
            whiteboardDataInfoObj.meetingId=whiteB_meeting_re.meetingId
        else:
            whiteboardDataInfoObj.iltId= whiteB_re.iltId
            whiteboardDataInfoObj.description= whiteB_re.description
            whiteboardDataInfoObj.meetingId=whiteboard.meetingId
        
        return  whiteboardDataInfoObj


    def update_ilts_whiteboard(self, user_id:int, iltId:int, meetingId:int, whiteboard:whiteboardData, db:Session):
        
        check_ilt_re = db.query(MdlIlts).filter(MdlIlts.id == iltId).one_or_none()
        check_meeting_re = db.query(MdlIltMeetings).filter(MdlIltMeetings.ilt_id==iltId,
                                         MdlIltMeetings.ilt_meeting_id==meetingId).one_or_none()
        
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meetingId).one_or_none()

        if check_ilt_re is None:
            raise CustomException(404,  "Ilt not found")   
        if check_meeting_re is None:
            raise CustomException(404,  "This meeting is not associated with Ilt") 
        if meeting_re.end_at is not None:
            raise CustomException(404,  "This meeting has been ended, we can not update it") 
        if user_id != meeting_re.note_taker_id and user_id != check_ilt_re.owner_id:
            raise CustomException(404,  "Only Ilt owner and Note Taker can update the data.")
        
        db_whiteB_re = db.query(MdlIltWhiteBoard).filter(MdlIltWhiteBoard.iltId == iltId).one_or_none()
        if db_whiteB_re is None:
            raise CustomException(404,  "No WhiteBoard for this Ilt.")

        db_whiteB_re.description = whiteboard.description
        db.commit()

        return {
                "statusCode": 200,
                "userMessage": "successfully updated description"
            }