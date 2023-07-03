from sqlalchemy.orm import Session
from app.models import MdlIltMeetings, MdlMeetings, MdlUsers, MdlIlts, \
    MdlIltMembers, MdlIltMeetingResponses, MdlMeetingsResponse,  \
    Mdl_updates, MdlIlt_ToDoTask, MdlIltissue, Mdl_issue
import sys
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from datetime import datetime, timezone, timedelta
from app.exceptions.customException import CustomException


def calculate_meeting_status(schedule_start_at, start_at, end_at):
    current_datetime = datetime.now(timezone.utc)
    if current_datetime < schedule_start_at and start_at == 0:
        return 0  # notStarted
    elif current_datetime >= start_at and end_at == 0:
        return 1  # inProgress
    else:
        return 2  # completed


class IltMeetingService:
    def get_upcomming_Ilts_meeting_list(self, user_id: int, ilt_id: int, db: Session):
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
                schedule_start_at = meeting_record.schedule_start_at.replace(
                    tzinfo=timezone.utc)
                start_meeting_time = meeting_record.start_at.replace(
                    tzinfo=timezone.utc) if meeting_record.start_at else 0
                end_meeting_time = meeting_record.end_at.replace(
                    tzinfo=timezone.utc) if meeting_record.end_at else 0
                print(start_meeting_time, end_meeting_time)
                status = calculate_meeting_status(
                    schedule_start_at, start_meeting_time, end_meeting_time)
                if status < 2:
                    ilt_list.append({
                                    "iltId": ilt_id,
                                    "iltMeetingId": meeting_record.id,
                                    "scheduledStartDate": meeting_record.schedule_start_at,
                                    "meetingStart": meeting_record.start_at,
                                    "meetingEnd": meeting_record.end_at,
                                    "location": meeting_record.location,
                                    "meetingStatus": status
                                    })
            return ilt_list
        else:
            raise CustomException(400,  "No meeting available for this Ilt id")

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
                         .all()]
        if list_meetings:
            ilt_list = []
            for mid in list_meetings:
                meeting_record = db.query(MdlMeetings).filter(
                    MdlMeetings.id == mid).one()
                schedule_start_at = meeting_record.schedule_start_at.replace(
                    tzinfo=timezone.utc)
                start_meeting_time = meeting_record.start_at.replace(
                    tzinfo=timezone.utc) if meeting_record.start_at else 0
                end_meeting_time = meeting_record.end_at.replace(
                    tzinfo=timezone.utc) if meeting_record.end_at else 0
                status = calculate_meeting_status(
                    schedule_start_at, start_meeting_time, end_meeting_time)

                val = {
                    "iltId": ilt_id,
                    "iltMeetingId": mid,
                    "scheduledStartDate": meeting_record.schedule_start_at,
                    "meetingStart": meeting_record.start_at,
                    "meetingEnd": meeting_record.end_at,
                    "location": meeting_record.location,
                    "meetingStatus": status
                }
                ilt_list.append(val)

            return ilt_list
        else:
            raise CustomException(400,  "No meeting available for this Ilt id")

    def create_ilts_meeting(self, ilt_id: int, user_id: int,  scheduledStartDate,
                            meetingStart, meetingEnd, db: Session, location: str):

        user_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if user_record is None:
            raise CustomException(404,  "User not found")
        Ilt_record = db.query(MdlIlts).filter(
            MdlIlts.id == ilt_id).one_or_none()
        if Ilt_record is None:
            raise CustomException(404,  "ILT not found")

        current_date = datetime.now(timezone.utc)
        if scheduledStartDate < current_date:
            raise CustomException(
                404, "please enter correct date, dates must be greater than currect data")

        db_meeting = MdlMeetings()
        db_meeting.schedule_start_at = scheduledStartDate
        if meetingStart:
            db_meeting.start_at = meetingStart
        if meetingEnd:
            db_meeting.end_at = meetingEnd
        if location:
            db_meeting.location = location

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
            ilt_id=ilt_id, ilt_meeting_id=db_meeting.id, )
        db.add(db_ilt_meeting)
        db.commit()
        db.refresh(db_ilt_meeting)
        return {
            "statusCode": 200,
            "userMessage": "meeting and corresponding meeting_response have successfully created"
        }

    def update_ilt_meeting(self, UserId: int, meeting_id: int, ilt_id: int, location, scheduledStartDate, meetingStart,
                           meetingEnd,  db: Session):
        if db.query(MdlUsers).filter(MdlUsers.id == UserId).one_or_none() is None:
            raise CustomException(404,  "userId did not found ")
        check_ilt_meeting_record = (db.query(MdlIltMeetings)
                                    .filter(MdlIltMeetings.ilt_id == ilt_id,
                                    MdlIltMeetings.ilt_meeting_id == meeting_id)
                                    .one_or_none())
        if check_ilt_meeting_record is None:
            raise CustomException(
                404,  "Meeting ID is not associated with ILT id")
        if scheduledStartDate < datetime.now(timezone.utc):
            raise CustomException(
                400,  "please enter correct date, dates must be greater than currect data")

        db_meeting = db.query(MdlMeetings).filter(
            MdlMeetings.id == meeting_id).one_or_none()
        if db_meeting is not None:
            db_meeting.location = location
            db_meeting.schedule_start_at = scheduledStartDate
            if meetingStart:
                db_meeting.start_at = meetingStart
            if meetingEnd:
                db_meeting.end_at = meetingEnd
            db.commit()
            db.refresh(db_meeting)
            return {
                "statusCode": 200,
                "userMessage": "meeting have successfully updated"
            }
        else:
            raise CustomException(404,  "meeting records not found")

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
                                     .filter(MdlIltMeetings.ilt_id == iltId,
                                             MdlIltMeetings.ilt_meeting_id == meeting_id)
                                     .one_or_none())
            if db_ilt_meeting_record is None:
                raise CustomException(
                    404,  "Meeting ID is not associated with ILT id")
            if ilt_record.owner_id == User_id:
                ilt_members_ids = [x.member_id for x in db.query(
                    MdlIltMembers).filter(MdlIltMembers.ilt_id == iltId).all()]
            else:
                check_ilt_user_map_record = (db.query(MdlIltMembers)
                                             .filter(MdlIltMembers.ilt_id == iltId, MdlIltMembers.member_id == User_id)
                                             .one_or_none())
                if check_ilt_user_map_record is None:
                    raise CustomException(
                        404,  "User ID is not associated with ILT")
                ilt_members_ids = [User_id]

            members_Info_dict = []
            meeting_response_id = 0

            for uid in ilt_members_ids:
                user_record = db.query(MdlUsers).filter(
                    MdlUsers.id == uid).one()
                meeting_response_row = db.query(MdlIltMeetingResponses)\
                    .filter(MdlIltMeetingResponses.meeting_id == meeting_id,
                            MdlIltMeetingResponses.meeting_user_id == uid).one_or_none()

                if meeting_response_row is None:
                    continue
                else:
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
                    .filter(MdlIltissue.meeting_response_id == meeting_response_id).all()
                user_issues_record = [db.query(Mdl_issue)
                                      .filter(Mdl_issue.id == record.id).one_or_none() for record in issue_record]  \
                    if issue_record else []

                members_Info_dict.append(
                    {
                        "iltMeetingResponseId": meeting_response_id,
                        "iltMeetingId": meeting_id,
                        "member": {
                            "userId": user_record.id,
                            "firstName": user_record.fname,
                            "lastName": user_record.lname,
                            "emailId": user_record.email
                        },
                        "attandance": meeting_response_record.attendance_flag,
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
                            "date": user_issues_single_record.created_at,
                            "resolvedFlag": user_issues_single_record.resolves_flag,
                            "recognizePerformanceFlag": user_issues_single_record.recognize_performance_flag,
                            "teacherSupportFlag": user_issues_single_record.teacher_support_flag,
                            "leaderSupportFlag": user_issues_single_record.leader_support_flag,
                            "advanceEqualityFlag": user_issues_single_record.advance_equality_flag,
                            "othersFlag": user_issues_single_record.others_flag
                        } for user_issues_single_record in user_issues_record]
                        if user_issues_record else []
                    }
                )

            return members_Info_dict
        except Exception as e:
            raise CustomException(500,  f"Internal server error {str(e)}")

    def start_ilt_meeting(self, UserId: int, meeting_id: int, ilt_id: int, db: Session):

        if db.query(MdlUsers).filter(MdlUsers.id == UserId).one_or_none() is None:
            raise CustomException(400,  "userId did not found ")
        if db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none() is None:
            raise CustomException(400,  "ilt_id did not found ")

        db_meeting = db.query(MdlMeetings).filter(
            MdlMeetings.id == meeting_id).one_or_none()
        if db_meeting is not None:
            db_meeting.start_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(db_meeting)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "meeting have started successfully"
            }
        else:
            raise CustomException(404,  "meeting records not found")

    def stop_ilt_meeting(self, UserId: int, meeting_id: int, ilt_id: int, db: Session):
        if db.query(MdlUsers).filter(MdlUsers.id == UserId).one_or_none() is None:
            raise CustomException(400,  "userId did not found ")
        if db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none() is None:
            raise CustomException(400,  "ilt_id did not found ")

        db_meeting = db.query(MdlMeetings).filter(
            MdlMeetings.id == meeting_id).one_or_none()
        if db_meeting is not None:
            db_meeting.end_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(db_meeting)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "meeting have successfully ended"
            }
        else:
            raise CustomException(400,  "meeting records not found")
