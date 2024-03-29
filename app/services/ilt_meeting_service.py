from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from app.models import MdlIltMeetings, MdlMeetings, MdlUsers, MdlIlts, \
    MdlIltMembers, MdlIltMeetingResponses, MdlMeetingsResponse,  MdlIlt_ToDoTask_map,\
    Mdl_updates, MdlIlt_ToDoTask, MdlIltissue, Mdl_issue, MdlIltMeetingWhiteBoard,\
    MdlIltWhiteBoard, MdlRocks, MdlRocks_members,  MdlEndMeetingRocks, MdlEndMeetingMemberRocks
from app.services.utils import get_upcomming_meeting, get_completed_issue_todo_list, inactivate_all_completed_issue_todo_list
import sys
from app.schemas.ilt_meeting_schemas import Status, whiteboardData, whiteboardDataInfo
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from datetime import datetime, timezone, timedelta
from app.exceptions.customException import CustomException
from app.services.utils import get_user_info

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

def update_rock(meeting_schedual_time, rock_created_time, db:Session):
    list_of_rock = db.query(MdlRocks).filter(MdlRocks.created_at == meeting_schedual_time).all()
    rock_records = []
    for db_rock in list_of_rock:
        db_rock.created_at = rock_created_time
        rock_records.append(db_rock)
    
    if rock_records:
        db.add_all(rock_records)
        db.commit()

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
        member_meeting_response_id_list = [meeting_response_id
                                           for meeting_response_id, in db.query(MdlIltMeetingResponses.meeting_response_id)
                                            .filter(MdlIltMeetingResponses.meeting_id==meeting_id,
                                                    MdlIltMeetingResponses.is_active==True)
                                            .all()]
        member_meeting_responce_records = [db.query(MdlMeetingsResponse)
                                                .filter(MdlMeetingsResponse.id==m_r_id).one() 
                                                for m_r_id in member_meeting_response_id_list]
        pending_issue_record_list = []
        pending_to_do_record_list = []
        for responceRecord in member_meeting_responce_records:
            meeting_response_id = responceRecord.id
            ##issue
            pending_issue_record_list.extend([id for id, in db.query(Mdl_issue.id)
                                        .join(MdlIltissue, Mdl_issue.id==MdlIltissue.issue_id )
                                        .filter(and_(MdlIltissue.meeting_response_id==meeting_response_id, 
                                                     Mdl_issue.resolves_flag==False, 
                                                     Mdl_issue.priority !=4, 
                                                     MdlIltissue.is_active==True))
                                        .all()])
            ##ToDo
            pending_to_do_record_list.extend([p_todo_id for p_todo_id, in db.query(MdlIlt_ToDoTask.id)
                                        .filter(and_(MdlIlt_ToDoTask.meeting_response_id==meeting_response_id,
                                                     MdlIlt_ToDoTask.status == False, 
                                                     MdlIlt_ToDoTask.is_active==True))
                                        .all()])        
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
        find_same_date_meeting = ((db
                                   .query(MdlMeetings)
                                   .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                   .filter(func.date(MdlMeetings.schedule_start_at) == scheduledStartDate.date(),
                                           MdlIltMeetings.ilt_id == ilt_id)).all())

        if len(find_same_date_meeting) == 1:
            raise CustomException(404,
                                  "Please select a different date; this one is already booked for a meeting.")
        if len(find_same_date_meeting) >= 2:
            raise CustomException(404,
                                  "This date has more that one meetings scheduled, please inform the administrator immediately")
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
                            .filter(MdlIltMembers.ilt_id == ilt_id,MdlIltMembers.is_active==True).all()]
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
             .join(MdlIltMeetings, MdlIltMeetings.ilt_meeting_id==MdlMeetings.id)
                .filter(MdlIltMeetings.ilt_id==ilt_id, MdlMeetings.end_at != None)
                .order_by(MdlMeetings.end_at.desc())
                .first())
        msg = "."
        if latest_meeting_re:
            if latest_meeting_re.end_at:
                print(latest_meeting_re.id)

                pending_issue_record_list, \
                pending_to_do_record_list = self.get_pending_issue_todo_ids(meeting_id=latest_meeting_re.id,
                                                                            db=db)
                if pending_issue_record_list or pending_to_do_record_list:
                    _success = self.transfer_ilt_meeting(meetingId=latest_meeting_re.id,ilt_id=ilt_id,
                                            UserId=user_id,
                                            listOfIssueIds= pending_issue_record_list, 
                                            listOfToDoIds = pending_to_do_record_list, 
                                            futureMeetingId= db_meeting.id, 
                                            check_end_meeting_flag= False,
                                            db=db)
                    msg = "with all Pending items from the last end meeting." 
                    # msg = "with all Pending items from the last meeting not tranferer."
            else:
                pass


        return {
            "statusCode": 200,
            "userMessage": f"meeting has been created {msg}"
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
            find_same_date_meeting = ((db
                                    .query(MdlMeetings)
                                    .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                    .filter(func.date(MdlMeetings.schedule_start_at) == scheduledStartDate.date(),
                                            MdlIltMeetings.ilt_id == ilt_id)).all())

            if len(find_same_date_meeting) >= 2:
                raise CustomException(404,
                                    "This date has more that one meetings scheduled, please inform the administrator immediately")
        
        db_meeting = db.query(MdlMeetings).filter(MdlMeetings.id == meeting_id).one_or_none()
        if db_meeting.end_at:
            raise CustomException(404,  "Meeting has been ended, Can not update it")
        
        if location:
            db_meeting.location = location
        if scheduledStartDate:
            if db_meeting.schedule_start_at != scheduledStartDate:
                update_rock(meeting_schedual_time=db_meeting.schedule_start_at,
                            rock_created_time=scheduledStartDate, db=db)
            db_meeting.schedule_start_at = scheduledStartDate
        if noteTakerId:
            db_meeting.note_taker_id = noteTakerId
        db.add(db_meeting)
        db.commit()
        return {
            "statusCode": 200,
            "userMessage": "meeting have successfully updated"
        }  

    def get_meeting_info(self, User_id: int, iltId: int, meeting_id: int,  db: Session):
        
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
                                       .filter(MdlIltMembers.ilt_id==iltId,
                                               MdlIltMembers.is_active==True)
                                       .all()]             
            if (User_id in current_ilt_members_ids) or (user.role_id in [4,3]):
                user_ids = [userId for userId, in db.query(MdlIltMeetingResponses.meeting_user_id)\
                    .filter(MdlIltMeetingResponses.meeting_id == meeting_id,
                            MdlIltMeetingResponses.is_active==True).all()]
                ilt_members_ids.extend(user_ids)
            else:
                raise CustomException( 404,  "Only Director, Project Leader and Ilt's Members can view the Ilt Info!")

            members_Info_dict = []
            meeting_response_id = 0
            noteTakerId = ilt_meeting_record.note_taker_id
            
            for uid in ilt_members_ids:
                user_record = db.query(MdlUsers).filter(
                    MdlUsers.id == uid).one()
                meeting_response_row = (db.query(MdlIltMeetingResponses)
                    .filter(and_(MdlIltMeetingResponses.meeting_id == meeting_id,
                            MdlIltMeetingResponses.meeting_user_id == uid,
                            MdlIltMeetingResponses.is_active==True)).one_or_none())
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
                    .filter(MdlIlt_ToDoTask.meeting_response_id == meeting_response_id,
                            MdlIlt_ToDoTask.is_active==True)\
                    .all()
                user_todolist_record = [
                    {
                        "todoListId": record.id,
                        "description": record.description,
                        "dueDate": record.due_date,
                        "status": record.status,
                        "isRepeat": True if (db.query(MdlIlt_ToDoTask)
                                             .filter(MdlIlt_ToDoTask.parent_to_do_id == record.id)
                                             .count() >= 1) else False,
                        "todoOwner": get_user_info(responceId=record.meeting_response_id, db=db),
                        "todoMemebers": [get_user_info(userId=map_re.user_id, db=db)
                                         for map_re in db.query(MdlIlt_ToDoTask_map)
                                         .filter(MdlIlt_ToDoTask_map.parent_to_do_id == (record.parent_to_do_id
                                                                                         if record.parent_to_do_id else record.id), 
                                                MdlIlt_ToDoTask_map.is_todo_member == True)
                                         .all()]
                    }
                    for record in todo_task_records
                ] if todo_task_records else []

                issue_record = (db.query(MdlIltissue)
                    .filter(MdlIltissue.meeting_response_id == meeting_response_id,
                            MdlIltissue.is_active==True)
                    .order_by(MdlIltissue.id.desc())
                    .all())

                user_issues_record = [db.query(Mdl_issue)
                                      .filter(Mdl_issue.id == record.issue_id).one_or_none() for record in issue_record]  \
                    if issue_record else []
                schedule_start_at = ilt_meeting_record.schedule_start_at
                start_meeting_time = ilt_meeting_record.start_at if ilt_meeting_record.start_at else 0
                end_meeting_time = ilt_meeting_record.end_at if ilt_meeting_record.end_at else 0
                meeting_status = calculate_meeting_status(schedule_start_at, 
                                                          start_meeting_time, 
                                                          end_meeting_time)
                # print("---",meeting_response_id, [(user_issues_single_record.created_at,
                #                                    user_issues_single_record.issue_resolve_date,
                #                                    user_issues_single_record.resolves_flag,
                #                                     user_issues_single_record.due_date - datetime.utcnow()) 
                #                                   for user_issues_single_record in user_issues_record])
                members_Info_dict.append(
                    {
                        "iltMeetingResponseId": meeting_response_id,
                        "iltMeetingId": meeting_id,
                        "iltMeetingLocation":ilt_meeting_record.location,
                        "meetingScheduleTime":ilt_meeting_record.schedule_start_at,
                        "noteTakerId":noteTakerId,
                        "meetingStatus":meeting_status,
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
                                                .filter(MdlIltissue.issue_id == user_issues_single_record.id,
                                                        MdlIltissue.is_active == True).count() > 1
                                                else False)
                        } for user_issues_single_record in user_issues_record]
                        if user_issues_record else []
                    }
                )
            return members_Info_dict

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
            raise CustomException(400,  "Meeting can start only after meeting schedule time. Please adjust the meeting schedule.")
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
        
    def stop_ilt_meeting(self, UserId: int, meeting_id: int, ilt_id: int, pastData_flag:bool, db: Session):
        user_re = db.query(MdlUsers).filter(MdlUsers.id == UserId).one_or_none()
        if user_re is None:
            raise CustomException(400,  "This user is not no longer exist.")
        if db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none() is None:
            raise CustomException(400,  "No Ilt present")
        
        ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==ilt_id).one_or_none()
        db_meeting = db.query(MdlMeetings).filter(MdlMeetings.id == meeting_id).one_or_none()
        if db_meeting is None:
            raise CustomException(400,  "Meeting records is not available")
        if UserId not in [db_meeting.note_taker_id, UserId != ownerId] and user_re.role_id != 4:
            raise CustomException(404,  "Only Ilt owner, Note Taker and Director can end the Meeting.")
        if db_meeting.start_at is None:
            raise CustomException(400,  "Meeting has not started")
        if db_meeting.end_at is not None:
            raise CustomException(400,  "Meeting is ended successfully")

        
        if db_meeting.start_at:
            db_meeting.end_at = datetime.utcnow() if pastData_flag == False else db_meeting.schedule_start_at + timedelta(hours=1)
            db.commit()
            db.refresh(db_meeting)
        # transfering 
        try:
            pending_issue_record_list, \
            pending_to_do_record_list = self.get_pending_issue_todo_ids(meeting_id=meeting_id,
                                                                        db=db)
            msg = self.transfer_ilt_meeting(meetingId=meeting_id, ilt_id=ilt_id, UserId=UserId,
                                            listOfIssueIds=pending_issue_record_list,
                                            listOfToDoIds=pending_to_do_record_list, futureMeetingId=0,
                                            db=db)
        except Exception as e:
            raise CustomException(
                400, "meeting has ended, unable to transefer pending Issues and TO-DO")
        #inactivating complete items
        (complete_issue_id_list,
            complete_to_do_id_list) = get_completed_issue_todo_list(meeting_id=meeting_id, db=db)
        inactivate_all_completed_issue_todo_list(listOfIssueIds=complete_issue_id_list,
                                                 listOfToDoIds=complete_to_do_id_list,
                                                 ilt_id=ilt_id,
                                                 db=db)
        # taking White Board snapshot for meeting(common View across all meeting)
        currect_des_of_whiteboard, = db.query(MdlIltWhiteBoard.description).filter(MdlIltWhiteBoard.iltId==ilt_id).one_or_none()
        db_whiteB = MdlIltMeetingWhiteBoard(description=currect_des_of_whiteboard, meetingId=meeting_id)
        db.add(db_whiteB)
        db.commit()
        db.refresh(db_whiteB)

        # taking snapshot of Rock status and members 
        get_ilt_rock =  db.query(MdlRocks).filter(MdlRocks.ilt_id==ilt_id).all()
        db_meeting_rock_re = [MdlEndMeetingRocks(rock_id=rock_re.id, 
                                              meeting_id = meeting_id, 
                                              rock_status=rock_re.on_track_flag,
                                              is_complete = True if db_meeting.end_at>rock_re.completed_at else False
                                              )
                            for rock_re in get_ilt_rock]
        db.add_all(db_meeting_rock_re)
        db.commit()
        for re in db_meeting_rock_re:
            get_rock_member_re = db.query(MdlRocks_members).filter(MdlRocks_members.ilt_rock_id==re.id).all()
            db_rock_member_re = [MdlEndMeetingMemberRocks(rock_id = re.id, 
                                                          meeting_id=meeting_id,
                                                          user_id = mem_re.user_id,
                                                          is_rock_owner = mem_re.is_rock_owner,
                                                          is_rock_member = mem_re.is_rock_member)
                                 for mem_re in get_rock_member_re]
            db.add_all(db_rock_member_re)
            db.commit()
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
                                                .filter(MdlIltMeetingResponses.meeting_id==meeting_id,
                                                        MdlIltMeetingResponses.is_active==True)
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
            
            return (num_of_attand_members,num_of_feedback_in_attand_members, [],
                     [], len(member_meeting_responce_records))
        
    def pending_issue_todo(self, UserId: int, meeting_id: int, ilt_id: int, db: Session):
        if db.query(MdlUsers).filter(MdlUsers.id == UserId).one_or_none() is None:
            raise CustomException(400,  "No users available ")
        if db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none() is None:
            raise CustomException(400,  "No Ilt present")

        meeting_re = db.query(MdlMeetings).filter(
            MdlMeetings.id == meeting_id).one_or_none()
        if meeting_re is None:
            raise CustomException(400, "Meeting records is not available")
        
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
                "attandiesFeedbackPercentage":attandiesFeedbackPercentage
                # "issues":pending_issue_record_list,
                # "todoList":pending_to_do_record_list,
                # "futureMeetings":future_meetings_list
            }

    def transfer_ilt_meeting(self, meetingId:int,ilt_id:int, UserId:int, 
                             listOfIssueIds:list, listOfToDoIds:list, futureMeetingId:int, 
                             db:Session, check_end_meeting_flag=True):
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
        upcomming_meeting_ids = get_upcomming_meeting(ilt_id=ilt_id, db=db) if futureMeetingId == 0 else [futureMeetingId]
        
        # transfering pending ilt
        for id in listOfIssueIds:
            map_re = (db.query(MdlIltissue).filter(MdlIltissue.issue_id==id, 
                                                   MdlIltissue.is_active==True)
                    .order_by(MdlIltissue.id.desc())
                    .first())        
            parent_responce_id= map_re.meeting_response_id 
            parent_user_id = (db.query(MdlIltMeetingResponses.meeting_user_id)
                            .filter(MdlIltMeetingResponses.meeting_response_id==parent_responce_id,
                                    MdlIltMeetingResponses.is_active==True)
                            .one_or_none()
                            )
            if parent_user_id is None:
                parent_user_id, = db.query(MdlIlts.owner_id).filter(MdlIlts.id ==ilt_id).one()
            else:
                parent_user_id, = parent_user_id
            
            list_of_user_meetingResponce = [db.query(MdlIltMeetingResponses.meeting_response_id,)
                                            .filter(MdlIltMeetingResponses.meeting_id == mid,
                                                    MdlIltMeetingResponses.meeting_user_id == parent_user_id,
                                                    MdlIltMeetingResponses.is_active==True)
                                            .one()[0] for mid in upcomming_meeting_ids
                                            ]
            list_of_user_meetingResponce =[ upcoming_meetingResponce
                                            for upcoming_meetingResponce in list_of_user_meetingResponce 
                                            if db.query(MdlIltissue)
                                                .filter(MdlIltissue.issue_id == id,
                                                        MdlIltissue.meeting_response_id == upcoming_meetingResponce,
                                                        MdlIltissue.is_active==True)
                                                .one_or_none() is None ]
            db_issue_records = [MdlIltissue(
                meeting_response_id=upcoming_meetingResponce,
                issue_id = id, 
                parent_meeting_responce_id=parent_responce_id,
                is_active=True) for upcoming_meetingResponce in list_of_user_meetingResponce]
            db.add_all(db_issue_records)
            db.commit()

        # transfering pending todo
        for todoid in listOfToDoIds:
            parent_todo_record = (db.query(MdlIlt_ToDoTask)
                                  .filter(MdlIlt_ToDoTask.id == todoid,
                                          MdlIlt_ToDoTask.is_active==True)
                                .one_or_none())
            if parent_todo_record is None:
                raise CustomException(400,  "records is not available")
            parent_to_do_id = parent_todo_record.parent_to_do_id if parent_todo_record.parent_to_do_id else parent_todo_record.id
            parent_user_id = (db.query(MdlIltMeetingResponses.meeting_user_id)
                                .filter(MdlIltMeetingResponses.meeting_response_id==parent_todo_record.meeting_response_id,
                                        MdlIltMeetingResponses.is_active==True)
                                .one_or_none()
                            )
            if parent_user_id is None:
                parent_user_id, = db.query(MdlIlts.owner_id).filter(MdlIlts.id ==ilt_id).one()
            else:
                parent_user_id, = parent_user_id
            list_of_user_meetingResponce = [db.query(MdlIltMeetingResponses.meeting_response_id,)
                                            .filter(MdlIltMeetingResponses.meeting_id == mid,
                                                    MdlIltMeetingResponses.meeting_user_id == parent_user_id,
                                                    MdlIltMeetingResponses.is_active==True)
                                            .one()[0] for mid in upcomming_meeting_ids
                                            ]
            verified_list_of_user_meetingResponce = [upcoming_meetingResponce
                                            for upcoming_meetingResponce in list_of_user_meetingResponce
                                            if not db.query(MdlIlt_ToDoTask)
                                            .filter(and_(MdlIlt_ToDoTask.parent_to_do_id == parent_to_do_id,
                                                    MdlIlt_ToDoTask.meeting_response_id == upcoming_meetingResponce,
                                                    MdlIlt_ToDoTask.is_active==True))
                                            .all()]
            db_todo_records = [MdlIlt_ToDoTask(
                                meeting_response_id=upcomming_m_re,
                                description=parent_todo_record.description, 
                                due_date=parent_todo_record.due_date, 
                                created_at= datetime.utcnow(),
                                status=parent_todo_record.status, 
                                parent_to_do_id=parent_to_do_id,
                                is_active=True) 
                               for upcomming_m_re in verified_list_of_user_meetingResponce]
            db.add_all(db_todo_records)
            db.commit()
            
    
        return {
                "statusCode": 200,
                "userMessage": "transfered successfully"
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
                                    .first())
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
    
    def insert_rock_info_for_all_end_meeting(self, update:bool, db:Session):
        if update==False:
            raise CustomException(500,"Bad Request.")
        # get_all_end_meeting_re = (db.query(MdlMeetings).filter(MdlMeetings.id == 29).all())
        get_all_end_meeting_re = (db.query(MdlMeetings).filter(MdlMeetings.end_at != None)
                                 .order_by(MdlMeetings.id).all())
        
        
        for db_meeting in get_all_end_meeting_re:
            meeting_id = db_meeting.id
            ilt_id, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id==db_meeting.id).one()
            get_ilt_rock =  db.query(MdlRocks).filter(MdlRocks.ilt_id==ilt_id).all()
            for rock_re in get_ilt_rock:
                if rock_re.created_at > db_meeting.schedule_start_at and rock_re.created_at !=db_meeting.schedule_start_at :
                    continue

                check_rock_re = (db.query(MdlEndMeetingRocks)
                                    .filter(MdlEndMeetingRocks.rock_id==rock_re.id, 
                                            MdlEndMeetingRocks.meeting_id==meeting_id)
                                    .one_or_none())
                get_rock_member_re = db.query(MdlRocks_members).filter(MdlRocks_members.ilt_rock_id==rock_re.id).all()
                if check_rock_re is  None:
                    if rock_re.is_complete:
                        is_complete = True if db_meeting.end_at>rock_re.completed_at  else False
                    else:
                        is_complete =  False
                    db_meeting_rock_re = MdlEndMeetingRocks(rock_id=rock_re.id, 
                                                        meeting_id = meeting_id, 
                                                        rock_status=rock_re.on_track_flag,
                                                        is_complete = is_complete)
                    db.add(db_meeting_rock_re)
                    db.commit()

                check_rock_mem_re = (db.query(MdlEndMeetingMemberRocks)
                                    .filter(MdlEndMeetingMemberRocks.rock_id==rock_re.id)
                                    .all())
                if len(check_rock_mem_re)==0:
                    db_rock_member_re = [MdlEndMeetingMemberRocks(rock_id = rock_re.id, 
                                                                meeting_id=meeting_id,
                                                                user_id = mem_re.user_id,
                                                                is_rock_owner = mem_re.is_rock_owner,
                                                                is_rock_member = mem_re.is_rock_member)
                                        for mem_re in get_rock_member_re]
                    db.add_all(db_rock_member_re)
                    db.commit()
                                    
        return{
            "statusCode": 200,
            "userMessage": "successfully updated"
        }
