from sqlalchemy.orm import Session
from app.models import MdlMeeting_rocks, MdlIlt_ToDoTask, Mdl_updates, \
    MdlMeetingsResponse, MdlIltMeetingResponses, MdlRocks, \
    Mdl_issue, MdlUsers, MdlIltissue, MdlMeetings, MdlIlts, \
    MdlIlt_rocks, MdlIltMembers, MdlIltMeetings, MdlPriorities
from sqlalchemy import desc, join
from typing import List, Optional
from app.schemas.meeting_response import MeetingResponse, Duedate
from datetime import datetime, timezone
from typing import Annotated, Union
from app.exceptions.customException import CustomException


class IltMeetingResponceService:
    def get_Ilts_meeting_list(self, user_id: int, meetingResponseId: int, db: Session):

        user = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if user is None:
            raise CustomException(404,  "User not found")
        MeetingsResponse = db.query(MdlMeetingsResponse).filter(
            MdlMeetingsResponse.id == meetingResponseId).one_or_none()
        if MeetingsResponse is None:
            raise CustomException(
                404,  "MeetingsResponse record not found")
        ilt_meet_re = db.query(MdlIltMeetingResponses)\
            .filter(MdlIltMeetingResponses.meeting_response_id == meetingResponseId).one()
        ilt_meet_id = ilt_meet_re.meeting_id
        user_meetingResponse_record = db.query(MdlMeetingsResponse)\
            .filter(MdlMeetingsResponse.id == meetingResponseId).first()
        user_record = db.query(MdlUsers).filter(
            MdlUsers.id == ilt_meet_re.meeting_user_id).one()

        members_Info_dict = {
            "userId": user_record.id,
            "firstName": user_record.fname,
            "lastName": user_record.lname,
            "emailId": user_record.email
        }
        user_update_record = [
            {
                "updateId": record.id,
                "description": record.description
            }
            for record in db.query(Mdl_updates)
                            .filter(Mdl_updates.meeting_response_id == meetingResponseId)
            .all()
        ]
        user_todolist_record = [
            {
                "todoListId": record.id,
                "description": record.description,
                "dueDate": record.due_date,
                "status": record.status
            } for record in db.query(MdlIlt_ToDoTask)
            .filter(MdlIlt_ToDoTask.meeting_response_id == meetingResponseId).all()]

        issue_record = db.query(MdlIltissue)\
            .filter(MdlIltissue.meeting_response_id == meetingResponseId).all()

        user_issues_record = [db.query(Mdl_issue)
                              .filter(Mdl_issue.id == record.id).one_or_none()
                              for record in issue_record]

        iltMeetingResponse_issues = ({
            "issueId": user_issues_single_record.id,
            "issue": user_issues_single_record.issue,
            "priorityId": user_issues_single_record.priority,
            "created_at": user_issues_single_record.created_at,
            "resolvedFlag": user_issues_single_record.resolves_flag,
            "recognizePerformanceFlag": user_issues_single_record.recognize_performance_flag,
            "teacherSupportFlag": user_issues_single_record.teacher_support_flag,
            "leaderSupportFlag": user_issues_single_record.leader_support_flag,
            "advanceEqualityFlag": user_issues_single_record.advance_equality_flag,
            "othersFlag": user_issues_single_record.others_flag
        } for user_issues_single_record in user_issues_record)

        return {
            "iltMeetingResponseId": meetingResponseId,
            "iltMeetingId": ilt_meet_id,
            "member": members_Info_dict,
            "attendance": user_meetingResponse_record.attendance_flag
            if user_meetingResponse_record.attendance_flag else None,
            "personalBest": user_meetingResponse_record.checkin_personal_best
            if user_meetingResponse_record.checkin_personal_best else "",
            "professionalBest": user_meetingResponse_record.checkin_professional_best
            if user_meetingResponse_record.checkin_professional_best else "",
            "rating": user_meetingResponse_record.rating if user_meetingResponse_record.rating else 0,
            "feedback": user_meetingResponse_record.feedback,
            "notes": user_meetingResponse_record.notes,
            "rockName": user_meetingResponse_record.rockName,
            "onTrack": user_meetingResponse_record.onTrack,
            "updates": user_update_record,
            "todoList": user_todolist_record,
            "issues": iltMeetingResponse_issues
        }

    def create_meeting_responses_empty_for_ILTmember(self, meeting_id: int, member_list: list, iltId: int, db: Session):
        try:
            for uid in member_list:
                db_meeting_response = MdlMeetingsResponse(attendance_flag=False, checkin_personal_best=None,
                                                          checkin_professional_best=None, rating=None,
                                                          feedback=None, notes=None, rockName=None, onTrack=False)
                db.add(db_meeting_response)
                db.commit()
                db.refresh(db_meeting_response)
                map_record = MdlIltMeetingResponses(meeting_id=meeting_id,
                                                    meeting_response_id=db_meeting_response.id, meeting_user_id=uid)
                db.add(map_record)
                db.commit()
                db.refresh(map_record)
                # create empaty rocks
                # db_meeting_response_rock = MdlMeeting_rocks(
                #     ilt_meeting_response_id=db_meeting_response.id)
                # db.add(db_meeting_response_rock)
                # db.commit()
                # db.refresh(db_meeting_response_rock)
                # if issue is last ended meeting unresolve in previous meeting
                # meeting_record = (
                #                 db.query(MdlMeetings)
                #                 .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                #                 .filter(MdlIltMeetings.ilt_id==iltId, MdlMeetings.schedule_start_at>current_dataTime)
                #                 .order_by(desc(MdlMeetings.end_at))
                #                 .first()
                #             )
                # if meeting_record

                # if uid in MdlIlt_rocks wrt ilt then add the rock id to the meeting_rosponce
                # user_ilt_map_record= (db.query(MdlIlt_rocks)
                #                         .filter(MdlIlt_rocks.ilt_id==iltId, MdlIlt_rocks.user_id==uid)
                #                         .all())
                # if user_ilt_map_record: # if present then add it the meetingResponce
                #     user_rock_ids = [record.ilt_rock_id for record in user_ilt_map_record]
                #     for rid in user_rock_ids:
                #         db_meeting_rocks = (MdlMeeting_rocks(   ilt_meeting_response_id=db_meeting_response.id,
                #                                                 rock_id = rid,
                #                                                 on_track_flag=False))
                #         db.add(db_meeting_rocks)
                #         db.commit()
                #         db.refresh(db_meeting_rocks)

            return (True, "")
        except Exception as e:
            return (False, str(e))

    def create_meeting_responses_empty_for_newMember_for_all_meetings(self, meeting_ids: list, member_list: list, db: Session):
        try:
            for mid in meeting_ids:
                for uid in member_list:
                    db_meeting_response = MdlMeetingsResponse(attendance_flag=None,
                                                              checkin_personal_best=None, checkin_professional_best=None,
                                                              rating=None, feedback=None, notes=None, rockName=None, onTrack=False)
                    db.add(db_meeting_response)
                    db.commit()
                    db.refresh(db_meeting_response)
                    map_record = MdlIltMeetingResponses(meeting_id=mid,
                                                        meeting_response_id=db_meeting_response.id, meeting_user_id=uid)
                    db.add(map_record)
                    db.commit()
                    db.refresh(map_record)

            return (True, "")
        except Exception as e:
            return (False, str(e))

    def create_meeting_responses(self, meeting_id: int, is_attand: bool, checkin_personal_best: str,
                                 checkin_professional_best: str, ratings: int, feedback: str, notes: str, db: Session):
        db_metting_response = MdlMeetingsResponse(attendance_flag=is_attand,
                                                  checkin_personal_best=checkin_personal_best, checkin_professional_best=checkin_professional_best,
                                                  rating=ratings, feedback=feedback, notes=notes, rockName=None, onTrack=False)
        db.add(db_metting_response)
        db.commit()
        db.refresh(db_metting_response)
        map_record = MdlIltMeetingResponses(
            meeting_id=meeting_id, meeting_response_id=db_metting_response.id)
        db.add(map_record)
        db.commit()
        db.refresh(map_record)
        return True

    def create_ilts_rocks(self, user_id: int, name: str, description: str, Ilt_id: int, db: Session):
        try:
            # check meetingResponseId
            user_re = db.query(MdlUsers).filter(
                MdlUsers.id == user_id).one_or_none()
            if user_re is None:
                raise CustomException(404,  "User_id not found")
            ilt_re = db.query(MdlIlts).filter(
                MdlIlts.id == Ilt_id).one_or_none()
            if ilt_re is None:
                raise CustomException(404,  "ilt_id not found")
            # db_rock = MdlRocks(name =name, description=description, on_track_flag=onTrack)
            db_rock = MdlRocks(ilt_id=Ilt_id, name=name,
                               description=description)
            db.add(db_rock)
            db.commit()
            db.refresh(db_rock)
            return {

                "statusCode": 200,
                "userMessage": "rock have successfully created inside the Ilt"
            }
        except Exception as e:
            raise CustomException(500, f"unable to create rock: {str(e)}")

    def read_ilt_rock(self, user_id: int, ilt_id: int, db: Session):
        try:
            check_user_id = db.query(MdlUsers).filter(
                MdlUsers.id == user_id).one_or_none()
            if check_user_id is None:
                raise CustomException(404,  "user_id did not exist!")
            check_ilt = db.query(MdlRocks).filter(
                MdlRocks.ilt_id == ilt_id).first()
            if not check_ilt:
                raise CustomException(
                    404,  "No rocks has created for this ilt_id")

            ilt_rock_records = [{"id": record.id,
                                "name": record.name,
                                 "description": record.description}
                                for record in db.query(MdlRocks)
                                .filter(MdlRocks.ilt_id == ilt_id)
                                .all()]
            return ilt_rock_records
        except Exception as e:
            raise CustomException(404,  f"unable to process your request{e}")

    def assign_ilts_rocks(self, logged_user_id: int, user_ids, Ilt_id: int, rock_id: int, rockOwnerId: int, db: Session):

        if db.query(MdlUsers).filter(MdlUsers.id == logged_user_id).one_or_none() is None:
            raise CustomException(400,  "logged userId is not found")
        rockOwner_Record = db.query(MdlUsers).filter(
            MdlUsers.id == rockOwnerId).one_or_none()
        if rockOwner_Record is None:
            raise CustomException(400,  "owner userId does not exist")
        user_ids = list(set(user_ids))
        for user_id in user_ids:
            ilt_member_exists = db.query(
                db.query(MdlIltMembers)
                .filter(MdlIltMembers.ilt_id == Ilt_id, MdlIltMembers.member_id == user_id)
                .exists()
            ).scalar()
            if not ilt_member_exists:
                raise CustomException(
                    404,  "record not found wrt user and ilt id, user is not a member of the ilt")
            else:
                pass

        check_ilt_inside_rock = db.query(
            db.query(MdlRocks)
            .filter(MdlRocks.ilt_id == Ilt_id, MdlRocks.id == rock_id)
            .exists()
        ).scalar()
        if not check_ilt_inside_rock:
            raise CustomException(
                400,  "this rock_id is not create inside ilt")
        db_rock_Record = db.query(MdlRocks).filter(
            MdlRocks.id == rockOwnerId).one()
        db_rock_Record.owner_id = rockOwnerId
        db.add(db_rock_Record)
        db.commit()
        db.refresh(db_rock_Record)
        try:
            for uid in user_ids:
                ownerStatus = False
                if uid == rockOwnerId:
                    ownerStatus = True
                db_ilt_rocks = MdlIlt_rocks(
                    ilt_id=Ilt_id, user_id=uid, ilt_rock_id=rock_id, is_rock_owner=ownerStatus)

                db.add(db_ilt_rocks)
                db.commit()
                db.refresh(db_ilt_rocks)
                db.close()
            return {

                "statusCode": 200,
                "userMessage": "rock is added to the corresponding user_id successfully with updated ownerId "
            }
        except Exception as e:
            raise CustomException(
                500,  f"unable to process your request, error {e}")

    def create_ilts_meeting_rocks(self, user_id: int, meetingResponseId: int, rockId: int,
                                  onTrack: bool, db: Session):
        try:
            user = db.query(MdlUsers).filter(
                MdlUsers.id == user_id).one_or_none()
            if user is None:
                raise CustomException(404,  "User not found")
            MeetingsResponse = db.query(MdlMeetingsResponse).filter(
                MdlMeetingsResponse.id == meetingResponseId).one_or_none()
            if MeetingsResponse is None:
                raise CustomException(
                    404,  "MeetingsResponse record not found")
            check_rock_re = db.query(MdlRocks).filter(
                MdlRocks.id == rockId).one_or_none()
            if check_rock_re is None:
                raise CustomException(404,  "please enter correct rock id")

            db_meeting_rocks = MdlMeeting_rocks(ilt_meeting_response_id=meetingResponseId,
                                                rock_id=rockId, on_track_flag=onTrack)
            db.add(db_meeting_rocks)
            db.commit()
            db.refresh(db_meeting_rocks)
            db.close()
            return {

                "statusCode": 200,
                "userMessage": "rock added to the corresponding meetingRosponse id successfully"
            }
        except Exception as e:
            raise CustomException(500,  f"unable to process your request {e}")

    def create_update_to_do_list(self, user_id: int, id: int, meetingResponseId: int, description: str,
                                 dueDate: Duedate, status: bool, db: Session):

        if db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none() is None:
            raise CustomException(400,  f" userId is not valid")
        if db.query(MdlMeetingsResponse).filter(MdlMeetingsResponse.id == meetingResponseId).one_or_none() is None:
            raise CustomException(400,  f" meetingResponseId is not valid")

        if id > 0:
            user_todo_record = (db.query(MdlIlt_ToDoTask)
                                .filter(MdlIlt_ToDoTask.meeting_response_id == meetingResponseId,
                                        MdlIlt_ToDoTask.id == id)
                                .one())
            user_todo_record.description = description
            user_todo_record.due_date = dueDate
            user_todo_record.status = status
            db.commit()
            db.refresh(user_todo_record)
        else:
            # check if user_id is inside MdlIltMembers
            db_meeting_todo = MdlIlt_ToDoTask(
                meeting_response_id=meetingResponseId, description=description, due_date=dueDate, status=status)
            db.add(db_meeting_todo)
            db.commit()
            db.refresh(db_meeting_todo)

        user_todolist_record = [
            {
                "todoListId": record.id,
                "description": record.description,
                "dueDate": record.due_date,
                "status": record.status
            } for record in db.query(MdlIlt_ToDoTask)
            .filter(MdlIlt_ToDoTask.meeting_response_id == meetingResponseId).all()]

        return {

            "statusCode": 200,
            "userMessage": "to-do list created successfully",
            "data": user_todolist_record
        }

    def create_meeting_update(self, user_id: int, id: int, meetingResponseId: int, description: str, db: Session):
        try:
            # checking if user_id is inside MdlUsers
            user = db.query(MdlUsers).filter(
                MdlUsers.id == user_id).one_or_none()
            if user is None:
                raise CustomException(404,  "User not found")
            if db.query(MdlMeetingsResponse).filter(MdlMeetingsResponse.id == meetingResponseId).one_or_none() is None:
                raise CustomException(400,  f" meetingResponseId is not valid")
            if id > 0:
                user_update_record = (db.query(Mdl_updates)
                                      .filter(Mdl_updates.meeting_response_id == meetingResponseId,
                                              Mdl_updates.id == id)
                                      .one())
                user_update_record.description = description
                db.commit()
                db.refresh(user_update_record)
            else:
                db_meeting_update = Mdl_updates(meeting_response_id=meetingResponseId,
                                                description=description)
                db.add(db_meeting_update)
                db.commit()
                db.refresh(db_meeting_update)

            user_update_record = [
                {
                    "updateId": record.id,
                    "description": record.description
                }
                for record in db.query(Mdl_updates)
                                .filter(Mdl_updates.meeting_response_id == meetingResponseId).all()
            ]

            return {
                "statusCode": 200,
                "userMessage": "updates has beem submited successfully",
                "data": user_update_record
            }
        except Exception as e:
            raise CustomException(
                500,  "unable to process your request {str(e)}")

    def create_update_issue(self, user_id: int, meetingResponseId: int, id: int, issue: str, priority: int,
                            created_at,
                            resolves_flag: bool,
                            recognize_performance_flag: bool,
                            teacher_support_flag: bool,
                            leader_support_flag: bool,
                            advance_equality_flag: bool,
                            others_flag: bool,
                            db: Session):

        
        # check if user_id is inside MdlIltMembers
        user = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if user is None:
            raise CustomException(404,  "User not found")
        responce_id = db.query(MdlMeetingsResponse).filter(
            MdlMeetingsResponse.id == meetingResponseId).one_or_none()
        if responce_id is None:
            raise CustomException(404,  "responce_id not found")

        if id:
            issue_map_re = (db.query(MdlIltissue)
                            .filter(MdlIltissue.meeting_response_id == meetingResponseId,
                                    MdlIltissue.issue_id == id)
                            .one())
            user_issue_record = (db.query(Mdl_issue)
                                    .filter(Mdl_issue.id == issue_map_re.issue_id).one())
            user_issue_record.issue = issue
            user_issue_record.priority = priority
            user_issue_record.created_at = created_at
            user_issue_record.resolves_flag = resolves_flag
            user_issue_record.recognize_performance_flag = recognize_performance_flag
            user_issue_record.teacher_support_flag = teacher_support_flag
            user_issue_record.leader_support_flag = leader_support_flag
            user_issue_record.advance_equality_flag = advance_equality_flag
            user_issue_record.others_flag = others_flag
            db.commit()
            db.refresh(user_issue_record)

        elif priority == 0:
            db_issue = Mdl_issue(issue=issue,
                                    created_at=created_at,
                                    resolves_flag=resolves_flag,
                                    recognize_performance_flag=recognize_performance_flag,
                                    teacher_support_flag=teacher_support_flag,
                                    leader_support_flag=leader_support_flag,
                                    advance_equality_flag=advance_equality_flag,
                                    others_flag=others_flag
                                    )
            db.add(db_issue)
            db.commit()
            db.refresh(db_issue)
            db_meeting_issue = MdlIltissue(
                meeting_response_id=meetingResponseId, issue_id=db_issue.id)
            db.add(db_meeting_issue)
            db.commit()
            db.refresh(db_meeting_issue)
        else:
            db_issue = Mdl_issue(issue=issue,
                                    priority=3 if priority==0 else priority,
                                    created_at=created_at,
                                    resolves_flag=resolves_flag,
                                    recognize_performance_flag=recognize_performance_flag,
                                    teacher_support_flag=teacher_support_flag,
                                    leader_support_flag=leader_support_flag,
                                    advance_equality_flag=advance_equality_flag,
                                    others_flag=others_flag
                                    )
            db.add(db_issue)
            db.commit()
            db.refresh(db_issue)
            db_meeting_issue = MdlIltissue(
                meeting_response_id=meetingResponseId, issue_id=db_issue.id, parent_meeting_responce_id=meetingResponseId)
            db.add(db_meeting_issue)
            db.commit()
            db.refresh(db_meeting_issue)

        issue_records = db.query(MdlIltissue)\
            .filter(MdlIltissue.meeting_response_id == responce_id.id).order_by(MdlIltissue.id.desc()).all()

        user_issue_records = [db.query(Mdl_issue)
                            .filter(Mdl_issue.id == record.id).one_or_none() for record in issue_records]  \
                if issue_records else []
        
        issues_records = [{
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
        } for user_issues_single_record in user_issue_records] if user_issue_records else []

        return {
            "statusCode": 200,
            "userMessage": "Issue have been created/modified successfully",
            "data": issues_records
        }

    def update_ilt_meeting_responses(self, data: MeetingResponse, db: Session
                                     ):
        """
            these are the keys inside 'data' object
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
                todoList: List[todoItem]
                issues: List[Issue],
        """
        try:
            try:
                meetingResponse = db.query(MdlMeetingsResponse).filter(
                    MdlMeetingsResponse.id == data.iltMeetingResponseId).one_or_none()
                if meetingResponse is None:
                    raise CustomException(
                        404,  "MeetingsResponse record did not found")
                # checking - is meeting stated
                ilt_meeting_record = (db.query(MdlMeetings)
                                      .filter(MdlMeetings.id == data.iltMeetingId).one_or_none())
                if ilt_meeting_record is None:
                    raise CustomException(404,  "meeting record did not found")
                # datetime.strptime(ilt_meeting_start_time, '%Y-%m-%d %H:%M:%S.%f')
                start_meeting_time = ilt_meeting_record.schedule_start_at
                end_meeting_time = ilt_meeting_record.end_at
                current_time = datetime.now()
                if current_time >= start_meeting_time and current_time <= end_meeting_time:
                    raise CustomException(
                        400,  "meeting has started, unable to process your requests")

                meetingResponseId = data.iltMeetingResponseId
                if (data.attendance != None) or data.personalBest or data.professionalBest or data.rating or data.feedback or data.notes:
                    user_meetingResponse_record = db.query(MdlMeetingsResponse)\
                        .filter(MdlMeetingsResponse.id == meetingResponseId).one()
                    if data.attendance != None:
                        user_meetingResponse_record.attendance_flag = data.attendance
                    if data.personalBest:
                        user_meetingResponse_record.checkin_personal_best = data.personalBest
                    if data.professionalBest:
                        user_meetingResponse_record.checkin_professional_best = data.professionalBest
                    if data.rating:
                        user_meetingResponse_record.rating = data.rating
                    if data.feedback:
                        user_meetingResponse_record.feedback = data.feedback
                    if data.notes:
                        user_meetingResponse_record.notes = data.notes
                    db.commit()
                    db.refresh(user_meetingResponse_record)

                if data.member:
                    if data.member.userId:
                        user_record = (db.query(MdlUsers)
                                       .filter(MdlUsers.id == data.member.userId)
                                       .one())
                        user_record.fname = data.member.firstName
                        user_record.lname = data.member.lastName
                        db.commit()
                        db.refresh(user_record)

                if data.rocks:
                    for i in range(len(data.rocks)):
                        if not data.rocks[i].rockId:
                            continue
                        user_rock = (db.query(MdlMeeting_rocks)
                                     .filter(MdlMeeting_rocks.ilt_meeting_response_id == meetingResponseId,
                                             MdlMeeting_rocks.rock_id == data.rocks[i].rockId)
                                     .one())
                        user_rock.on_track_flag = data.rocks[i].onTrack
                        db.commit()
                        db.refresh(user_rock)
                if data.updates:
                    for i in range(len(data.updates)):
                        if not data.updates[i].id:
                            continue
                        user_update_record = (db.query(Mdl_updates)
                                              .filter(Mdl_updates.meeting_response_id == meetingResponseId,
                                                      Mdl_updates.id == data.updates[i].id)
                                              .one())
                        user_update_record.description = data.updates[i].description
                        db.commit()
                        db.refresh(user_update_record)

                if data.todoList:
                    for i in range(len(data.todoList)):
                        if not data.todoList[i].id:
                            continue
                        user_todo_record = (db.query(MdlIlt_ToDoTask)
                                            .filter(MdlIlt_ToDoTask.meeting_response_id == meetingResponseId,
                                                    MdlIlt_ToDoTask.id == data.todoList[i].id)
                                            .one())
                        user_todo_record.description = data.todoList[i].description
                        user_todo_record.due_date = data.todoList[i].dueDate
                        user_todo_record.status = data.todoList[i].status
                        db.commit()
                        db.refresh(user_todo_record)

                if data.issues:
                    for i in range(len(data.updates)):
                        if not data.issues[i].issueid:
                            continue
                        issue_map_re = (db.query(MdlIltissue)
                                        .filter(MdlIltissue.meeting_response_id == meetingResponseId,
                                                MdlIltissue.issue_id == data.issues[i].issueid)
                                        .one())
                        user_issue_record = (db.query(Mdl_issue)
                                             .filter(Mdl_issue.id == issue_map_re.issue_id).one())

                        user_issue_record.id = data.issues[i].issueid
                        user_issue_record.issue = data.issues[i].issue
                        user_issue_record.priority = data.issues[i].priorityId
                        user_issue_record.created_at = data.issues[i].created_at
                        user_issue_record.resolves_flag = data.issues[i].resolvedFlag
                        user_issue_record.recognize_performance_flag = data.issues[
                            i].recognizePerformanceFlag
                        user_issue_record.teacher_support_flag = data.issues[i].teacherSupportFlag
                        user_issue_record.leader_support_flag = data.issues[i].leaderSupportFlag
                        user_issue_record.advance_equality_flag = data.issues[i].advanceEqualityFlag
                        user_issue_record.others_flag = data.issues[i].othersFlag
                        db.commit()
                        db.refresh(user_issue_record)

            except Exception as e:
                raise CustomException(
                    404,  f"all details with corresponding meeting responceId is not found, error - {str(e)}")

            return {

                "statusCode": 200,
                "userMessage": "we have successfully added all records"
            }
        except Exception as e:
            raise CustomException(500,  f"Internal Server Error = {str(e)}")

    def update_meetingResponce_rocks(self, user_id: int,
                                     meetingResponseId: int,
                                     name: str,
                                     onTrack: bool,
                                     db: Session):
        if db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none() is None:
            raise CustomException(400,  f"invaild users")

        user_meetingResponse_record = (db.query(MdlMeetingsResponse)
                                       .filter(MdlMeetingsResponse.id == meetingResponseId)
                                       .one_or_none())
        if user_meetingResponse_record is None:
            raise CustomException(
                404,  "MeetingsResponse record did not found")

        if name:
            user_meetingResponse_record.rockName = name
        if onTrack:
            user_meetingResponse_record.onTrack = onTrack

        db.commit()
        db.refresh(user_meetingResponse_record)

        return {
            "statusCode": 200,
            "userMessage": "Rock Updated successfully"
        }

    def update_meetingResponce_checkin(self, user_id: int,
                                       meetingResponseId: int,
                                       personalBest: str,
                                       professionalBest: str,
                                       attendance: bool,
                                       db: Session):

        check_user_id = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if check_user_id is None:
            raise CustomException(404,  "User not found")

        user_meetingResponse_record = (db.query(MdlMeetingsResponse)
                                       .filter(MdlMeetingsResponse.id == meetingResponseId)
                                       .one_or_none())
        if user_meetingResponse_record is None:
            raise CustomException(
                404,  "MeetingsResponse record did not found")

        # user_meetingResponse_record = db.query(MdlMeetingsResponse)\
        #                                         .filter(MdlMeetingsResponse.id==meetingResponseId).one()
        if personalBest:
            user_meetingResponse_record.checkin_personal_best = personalBest
        if professionalBest:
            user_meetingResponse_record.checkin_professional_best = professionalBest

        user_meetingResponse_record.attendance_flag = attendance

        db.commit()
        db.refresh(user_meetingResponse_record)
        return {
            "statusCode": 200,
            "userMessage": "Updated successfully"
        }

    def update_meetingResponce_feedbacks(self, user_id: int,
                                         meetingResponseId: int,
                                         rating: int,
                                         feedback: str,
                                         notes: str,
                                         db: Session):
        check_user_id = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if check_user_id is None:
            raise CustomException(404,  "User not found")

        user_meetingResponse_record = (db.query(MdlMeetingsResponse)
                                       .filter(MdlMeetingsResponse.id == meetingResponseId)
                                       .one_or_none())
        if user_meetingResponse_record is None:
            raise CustomException(
                404,  "MeetingsResponse record did not found")

        user_meetingResponse_record.attendance_flag = True
        if rating:
            user_meetingResponse_record.rating = rating
        if feedback:
            user_meetingResponse_record.feedback = feedback
        if notes:
            user_meetingResponse_record.notes = notes
        db.commit()
        db.refresh(user_meetingResponse_record)
        return {
            "statusCode": 200,
            "userMessage": "Updated successfully"
        }
