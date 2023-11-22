from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from app.models import MdlIlt_ToDoTask, Mdl_updates, \
    MdlMeetingsResponse, MdlIltMeetingResponses, MdlRocks, \
    Mdl_issue, MdlUsers, MdlIltissue, MdlMeetings, MdlIlts, \
    MdlRocks_members, MdlIltMembers, MdlIltMeetings, MdlPriorities
from sqlalchemy import desc, join
from typing import List, Optional
from app.schemas.meeting_response import MeetingResponse, Duedate, RockInput, RockOutput, Member
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
            "advanceEquityFlag": user_issues_single_record.advance_equality_flag,
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
            member_list = list(set(member_list))
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
   
    def read_ilt_rock(self, user_id: int, ilt_id: int, meeting_id: int,  db: Session):
        check_user_id = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        if check_user_id is None:
            raise CustomException(404,  "user_id did not exist!")
        
        if db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none() is None:
            raise CustomException(404,  "Ilt not found")
        meeting_re = (db.query(MdlMeetings)
                        .filter(MdlMeetings.id==meeting_id)
                        .one_or_none())
        list_rocks_re = (db.query(MdlRocks).filter(MdlRocks.ilt_id == ilt_id
                                                   ,MdlRocks.created_at < meeting_re.schedule_start_at
                                                   )
                                    .all())
        meeting_rock_records = []
        for record in list_rocks_re:
            rockObj = RockOutput()
            rockObj.rockId =record.id
            rockObj.iltId = record.ilt_id
            rockObj.name = record.name
            rockObj.description = record.description
            rockObj.onTrack = record.on_track_flag
            rockObj.isComplete = record.is_complete

            rockObj.rockOwner = [Member(userId=u_re.id, firstName=u_re.fname, lastName=u_re.lname)
                                 for u_re in db.query(MdlUsers)
                                 .join(MdlRocks_members, MdlUsers.id == MdlRocks_members.user_id)
                                 .filter(MdlRocks_members.ilt_rock_id == record.id,
                                         MdlRocks_members.is_rock_owner == True)
                                 .all()
                                 ]
            
            rockObj.rockMembers = [Member(userId=u_re.id, firstName=u_re.fname, lastName=u_re.lname)
                                    for u_re in db.query(MdlUsers)
                                    .join(MdlRocks_members, MdlUsers.id == MdlRocks_members.user_id)
                                    .filter(MdlRocks_members.ilt_rock_id == record.id,
                                            MdlRocks_members.is_rock_member == True)
                                    .all()
                                ]
           
            meeting_rock_records.append(rockObj)

        return meeting_rock_records

    
    def create_assign_update_rock(self, rockData:RockInput, user_id, meeting_id, db:Session):

        if db.query(MdlIlts).filter(MdlIlts.id == rockData.iltId).one_or_none() is None:
            raise CustomException(404,  "ilt not found")
        if db.query(MdlIltMembers).filter(and_(MdlIltMembers.ilt_id==rockData.iltId,MdlIltMembers.member_id == rockData.rockOwnerId)
                                          ).one_or_none() is None:
            raise CustomException(400,  "Rock owner not found.")
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id ==meeting_id).one_or_none()
        if meeting_re is None:
             raise CustomException(400,  "Meeting not found.")
        user_re = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        if user_re is None:
            raise CustomException(404,  "User not found")
        #verify each member
        rockMembers = rockData.rockMembers
        rockMembers.append(rockData.rockOwnerId)
        unique_user_ids = list(set(rockMembers))

        ilt_member_count = (db.query(MdlIltMembers)
                            .filter(MdlIltMembers.ilt_id == rockData.iltId, MdlIltMembers.member_id.in_(unique_user_ids))
                            .count())
        if ilt_member_count != len(unique_user_ids):
            raise CustomException(
                404, "Record not found for some users. They are not members of the ILT")
        rock_name = rockData.name.strip().lower()
        check_title = (db.query(MdlRocks).filter(and_(MdlRocks.ilt_id == rockData.iltId,
                                                      func.lower(MdlRocks.name) == rock_name))
                       .all())
        if rockData.rockId:
            #update
            
            rock_id = rockData.rockId
            db_rock = db.query(MdlRocks).filter(and_(MdlRocks.id==rock_id, MdlRocks.ilt_id==rockData.iltId)).one_or_none()
            if db_rock.name.lower() !=rockData.name.strip().lower(): 
                if check_title:
                    raise CustomException(404, "Rock Already Exists, Please change Rock Name")
            db_rock.name = rockData.name.strip()
            db_rock.description = rockData.description
            db_rock.is_complete = rockData.isComplete
            db_rock.updated_at = datetime.utcnow()
            db_rock.on_track_flag = rockData.onTrack
            db.add(db_rock)
            db.commit()
            db.refresh(db_rock)

            current_rock_member = [u_id for u_id, in db.query(MdlRocks_members.user_id)
                                    .filter(MdlRocks_members.ilt_rock_id == rock_id, 
                                            # MdlRocks_members.user_id.in_(unique_user_ids),
                                            or_(MdlRocks_members.is_rock_member ==True,
                                            MdlRocks_members.is_rock_owner ==True)
                                            )
                                        .all()]
            # db_change_owner = (db.query(MdlRocks_members)
            #                     .filter(and_(MdlRocks_members.ilt_rock_id==rock_id,
            #                                 MdlRocks_members.user_id ==rockData.rockOwnerId
            #                                                                             ))
            #                     .one_or_none())
            # if db_change_owner is not None:
            #     db_change_owner.is_rock_owner = True
            #     db_change_owner.is_rock_member = False
            #     db.add(db_change_owner)
            #     db.commit()
            #     db.refresh(db_change_owner)

            db_current_owner = (db.query(MdlRocks_members)
                                .filter(and_(MdlRocks_members.ilt_rock_id==rock_id,
                                        MdlRocks_members.is_rock_owner==True))
                                .one_or_none())
            
            
            if rockData.rockOwnerId != db_current_owner.user_id:
                db_current_owner.is_rock_owner = False 
                db_current_owner.is_rock_member = True 
                db.add(db_current_owner)
                db.commit()
                db.refresh(db_current_owner)
                db_change_owner = (db.query(MdlRocks_members)
                                .filter(and_(MdlRocks_members.ilt_rock_id==rock_id,
                                            MdlRocks_members.user_id ==rockData.rockOwnerId
                                            ))
                                .one_or_none())
                if db_change_owner is not None:
                    db_change_owner.is_rock_owner = True
                    db_change_owner.is_rock_member = False
                    db.add(db_change_owner)
                    db.commit()
                    db.refresh(db_change_owner)

            
            if len(unique_user_ids) != len(current_rock_member):
                new_user = set(unique_user_ids)-set(current_rock_member)
                remove_user = set(current_rock_member) - set(unique_user_ids)
                new_user_records = []
                for u_id in new_user:
                    db_rock_user = (db.query(MdlRocks_members)
                                .filter(and_(MdlRocks_members.user_id==u_id,
                                                                     MdlRocks_members.ilt_rock_id==rock_id))
                                .one_or_none())
                    if db_rock_user is None:
                        new_user_records.append(MdlRocks_members(user_id=u_id,
                                                           ilt_rock_id = rock_id,
                                                           is_rock_owner = (u_id == rockData.rockOwnerId),
                                                           is_rock_member = (u_id != rockData.rockOwnerId)))
                    else:
                        db_rock_user.is_rock_member = (u_id != rockData.rockOwnerId)
                        db_rock_user.is_rock_owner = (u_id == rockData.rockOwnerId)
                        db.add(db_rock_user)
                        db.commit()
                        db.refresh(db_rock_user)

                if new_user_records:
                    db.add_all(new_user_records)
                    db.commit()
                    # db.refresh(new_user_records)

                for u_id in remove_user:
                    db_rock_user_remove = (db.query(MdlRocks_members)
                                    .filter(and_(MdlRocks_members.user_id == u_id,
                                                 MdlRocks_members.ilt_rock_id == rock_id))
                                    .one_or_none())
                    db_rock_user_remove.is_rock_owner = False
                    db_rock_user_remove.is_rock_member = False
                    db.add(db_rock_user_remove)
                    db.commit()
                    db.refresh(db_rock_user_remove)
                
                
            return {
                "statusCode": 200,
                "userMessage": "Updated Successfully"
            }

        if check_title:
            raise CustomException(404, "Rock Already Exists, Please change Rock Name")
        
        # create
        db_rock = MdlRocks(ilt_id=rockData.iltId, 
                           name=rockData.name, 
                           description=rockData.description, 
                           is_complete =False,
                           created_at = meeting_re.schedule_start_at,
                           on_track_flag = rockData.onTrack)
        
        db.add(db_rock)
        db.commit()
        db.refresh(db_rock)
        rock_id = db_rock.id

        # assign
        check_ilt_inside_rock = db.query(MdlRocks.id).filter(and_(MdlRocks.ilt_id == rockData.iltId, MdlRocks.id == rock_id)).one_or_none()
        if check_ilt_inside_rock is None:
            raise CustomException(400,  "unable to create rock")
        
        rock_objects = [
            MdlRocks_members(
                user_id=uid,
                ilt_rock_id=rock_id,
                is_rock_owner=(uid == rockData.rockOwnerId),
                is_rock_member = (uid != rockData.rockOwnerId)
            )
            for uid in unique_user_ids
        ]
        db.add_all(rock_objects)
        db.commit()
        db.refresh(rock_objects)

        return {
            "statusCode": 200,
            "userMessage": "Rock added to the corresponding meetingRosponse id successfully"
        }


    def create_update_to_do_list(self, user_id: int, id: int, meetingResponseId: int, description: str,
                                 dueDate: Duedate, status: bool, db: Session):

        if db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none() is None:
            raise CustomException(400,  f" userId is not valid")
        if db.query(MdlMeetingsResponse).filter(MdlMeetingsResponse.id == meetingResponseId).one_or_none() is None:
            raise CustomException(400,  f" meetingResponseId is not valid")
        meeting_id,  = db.query(MdlIltMeetingResponses.meeting_id).filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId).one()
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one_or_none()
        if meeting_re.start_at and meeting_re.end_at is None:
            iltId, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id==meeting_id).one_or_none()
            ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==iltId).one_or_none()
            if user_id != meeting_re.note_taker_id and user_id != ownerId:
                raise CustomException(404,  "Only Ilt owner and Note Taker can edit the data.")
        if meeting_re.end_at:
            raise CustomException(404,  "This meeting has been end, We can not update it.")
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
                meeting_response_id=meetingResponseId, description=description, due_date=dueDate, status=status, 
                created_at= datetime.utcnow())
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
            "userMessage": "Created/Updated successfully",
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
            meeting_id,  = db.query(MdlIltMeetingResponses.meeting_id).filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId).one()
            meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one_or_none()
            if meeting_re.start_at and meeting_re.end_at is None:
                iltId, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id==meeting_id).one_or_none()
                ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==iltId).one_or_none()
                if user_id != meeting_re.note_taker_id and user_id != ownerId:
                    raise CustomException(404,  "Only Ilt owner and Note Taker can edit the data.")
                    
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

    def create_update_issue(self, user_id: int, meetingResponseId: int, id: int,meeting_id:int,  issue: str, priority: int,
                            due_date,
                            resolves_flag: bool,
                            recognize_performance_flag: bool,
                            teacher_support_flag: bool,
                            leader_support_flag: bool,
                            advance_equality_flag: bool,
                            others_flag: bool,
                            assign_to_responce_id:int,
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
        check_assign_to_responce_id = db.query(MdlIltMeetingResponses).filter(and_(MdlIltMeetingResponses.meeting_id==meeting_id,
                                                                                   MdlIltMeetingResponses.meeting_response_id==assign_to_responce_id)).one_or_none()
        if check_assign_to_responce_id is None:
            raise CustomException(404,  "This responce_id is not associated with This Meeting.")
        
        meeting_id_,  = db.query(MdlIltMeetingResponses.meeting_id).filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId).one()
        if meeting_id_ != meeting_id:
             raise CustomException(404,  "invalid Meeting Id")
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one_or_none()
        if meeting_re.start_at and meeting_re.end_at is None:
            iltId, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id==meeting_id).one_or_none()
            ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==iltId).one_or_none()
            if user_id != meeting_re.note_taker_id and user_id != ownerId:
                raise CustomException(404,  "Only Ilt owner and Note Taker can edit the data.")
        if meeting_re.end_at:
            raise CustomException(404,  "This meeting has been end, We can not update it.")
        
        if id:
            if assign_to_responce_id:

                meeting_responcesId_list = [r_id for r_id, in db.query(MdlIltMeetingResponses.meeting_response_id)
                                            .filter(MdlIltMeetingResponses.meeting_id == meeting_id)
                                            .all()]
                # print("----------",meeting_responcesId_list)
                db_issue_latest_re = (db.query(MdlIltissue)
                                      .filter(and_(MdlIltissue.issue_id == id,
                                                   MdlIltissue.meeting_response_id.in_(meeting_responcesId_list)))).one_or_none()
                # print(db_issue_latest_re.meeting_response_id, assign_to_responce_id)
                if db_issue_latest_re.meeting_response_id != assign_to_responce_id:
                    db_issue_latest_re.meeting_response_id = assign_to_responce_id
                    db.commit()
                    db.refresh(db_issue_latest_re)

            issue_map_re = (db.query(MdlIltissue)
                            .filter(and_(MdlIltissue.meeting_response_id == db_issue_latest_re.meeting_response_id,
                                    MdlIltissue.issue_id == id))
                            .one())
            
            user_issue_record = (db.query(Mdl_issue)
                                    .filter(Mdl_issue.id == issue_map_re.issue_id).one())
            user_issue_record.issue = issue
            user_issue_record.priority = priority
            user_issue_record.due_date = due_date
            user_issue_record.issue_resolve_date = datetime.utcnow() if resolves_flag==True else None 
            user_issue_record.resolves_flag = resolves_flag
            user_issue_record.recognize_performance_flag = recognize_performance_flag
            user_issue_record.teacher_support_flag = teacher_support_flag
            user_issue_record.leader_support_flag = leader_support_flag
            user_issue_record.advance_equality_flag = advance_equality_flag
            user_issue_record.others_flag = others_flag
            db.commit()
            db.refresh(user_issue_record)
            #get all responcesId from current meeting, 

            
        else:
            db_issue = Mdl_issue(issue=issue,
                                    priority=priority,
                                    created_at=datetime.utcnow(),
                                    due_date= due_date, 
                                    issue_resolve_date = datetime.utcnow() if resolves_flag==True else None,
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

            # meeting_id, = (db.query(MdlIltMeetingResponses.meeting_id)
            #                                 .filter(MdlIltMeetingResponses.meeting_response_id == meetingResponseId)
            #                                 .one())
            # assignto_responce_id, = (db.query(MdlIltMeetingResponses.meeting_response_id)
            #                          .filter(and_(MdlIltMeetingResponses.meeting_id == meeting_id,
            #                                       MdlIltMeetingResponses.meeting_user_id == assign_to_responce_id)
            #                                  )
            #                          )

            db_meeting_issue = MdlIltissue(
                meeting_response_id=assign_to_responce_id, issue_id=db_issue.id, parent_meeting_responce_id=assign_to_responce_id)
            db.add(db_meeting_issue)
            db.commit()
            db.refresh(db_meeting_issue)

        issue_records = db.query(MdlIltissue)\
            .filter(MdlIltissue.meeting_response_id == responce_id.id).order_by(MdlIltissue.id.desc()).all()

        user_issue_records = [db.query(Mdl_issue)
                            .filter(Mdl_issue.id == record.issue_id).one_or_none() for record in issue_records]  \
                if issue_records else []
        
        issues_records = [{
            "issueId": user_issues_single_record.id,
            "issue": user_issues_single_record.issue,
            "priorityId": user_issues_single_record.priority,
            "date": user_issues_single_record.due_date,
            "resolvedFlag": user_issues_single_record.resolves_flag,
            "recognizePerformanceFlag": user_issues_single_record.recognize_performance_flag,
            "teacherSupportFlag": user_issues_single_record.teacher_support_flag,
            "leaderSupportFlag": user_issues_single_record.leader_support_flag,
            "advanceEquityFlag": user_issues_single_record.advance_equality_flag,
            "othersFlag": user_issues_single_record.others_flag
        } for user_issues_single_record in user_issue_records] if user_issue_records else []

        return {
            "statusCode": 200,
            "userMessage": "Issue have been created/modified successfully",
            "data": issues_records
        }

    # def update_ilt_meeting_responses(self, data: MeetingResponse, db: Session
    #                                  ):
    #     """
    #         these are the keys inside 'data' object
    #             iltMeetingResponseId: int 
    #             iltMeetingId ==> 
    #             member: members ==>
    #             attendance: bool,
    #             personalBest: str,
    #             professionalBest: str
    #             rating: int
    #             feedback: str
    #             notes: str
    #             rocks: List[Rock]
    #             updates: List[str]
    #             todoList: List[todoItem]
    #             issues: List[Issue],
    #     """
    #     try:
    #         try:
    #             notUse = True
    #             if notUse:
    #                 raise CustomException(404,  "Not in use")
    #             meetingResponse = db.query(MdlMeetingsResponse).filter(
    #                 MdlMeetingsResponse.id == data.iltMeetingResponseId).one_or_none()
    #             if meetingResponse is None:
    #                 raise CustomException(
    #                     404,  "MeetingsResponse record did not found")
                
    #             # checking - is meeting stated
    #             ilt_meeting_record = (db.query(MdlMeetings)
    #                                   .filter(MdlMeetings.id == data.iltMeetingId).one_or_none())
    #             if ilt_meeting_record is None:
    #                 raise CustomException(404,  "meeting record did not found")
    #             # datetime.strptime(ilt_meeting_start_time, '%Y-%m-%d %H:%M:%S.%f')
    #             start_meeting_time = ilt_meeting_record.schedule_start_at
    #             end_meeting_time = ilt_meeting_record.end_at
    #             current_time = datetime.now()
    #             if current_time >= start_meeting_time and current_time <= end_meeting_time:
    #                 raise CustomException(
    #                     400,  "meeting has started, unable to process your requests")

    #             meetingResponseId = data.iltMeetingResponseId
    #             if (data.attendance != None) or data.personalBest or data.professionalBest or data.rating or data.feedback or data.notes:
    #                 user_meetingResponse_record = db.query(MdlMeetingsResponse)\
    #                     .filter(MdlMeetingsResponse.id == meetingResponseId).one()
    #                 if data.attendance != None:
    #                     user_meetingResponse_record.attendance_flag = data.attendance
    #                 if data.personalBest:
    #                     user_meetingResponse_record.checkin_personal_best = data.personalBest
    #                 if data.professionalBest:
    #                     user_meetingResponse_record.checkin_professional_best = data.professionalBest
    #                 if data.rating:
    #                     user_meetingResponse_record.rating = data.rating
    #                 if data.feedback:
    #                     user_meetingResponse_record.feedback = data.feedback
    #                 if data.notes:
    #                     user_meetingResponse_record.notes = data.notes
    #                 db.commit()
    #                 db.refresh(user_meetingResponse_record)

    #             if data.member:
    #                 if data.member.userId:
    #                     user_record = (db.query(MdlUsers)
    #                                    .filter(MdlUsers.id == data.member.userId)
    #                                    .one())
    #                     user_record.fname = data.member.firstName
    #                     user_record.lname = data.member.lastName
    #                     db.commit()
    #                     db.refresh(user_record)

    #             if data.rocks:
    #                 for i in range(len(data.rocks)):
    #                     if not data.rocks[i].rockId:
    #                         continue
    #                     user_rock = (db.query(MdlMeeting_rocks)
    #                                  .filter(MdlMeeting_rocks.ilt_meeting_response_id == meetingResponseId,
    #                                          MdlMeeting_rocks.rock_id == data.rocks[i].rockId)
    #                                  .one())
    #                     user_rock.on_track_flag = data.rocks[i].onTrack
    #                     db.commit()
    #                     db.refresh(user_rock)
    #             if data.updates:
    #                 for i in range(len(data.updates)):
    #                     if not data.updates[i].id:
    #                         continue
    #                     user_update_record = (db.query(Mdl_updates)
    #                                           .filter(Mdl_updates.meeting_response_id == meetingResponseId,
    #                                                   Mdl_updates.id == data.updates[i].id)
    #                                           .one())
    #                     user_update_record.description = data.updates[i].description
    #                     db.commit()
    #                     db.refresh(user_update_record)

    #             if data.todoList:
    #                 for i in range(len(data.todoList)):
    #                     if not data.todoList[i].id:
    #                         continue
    #                     user_todo_record = (db.query(MdlIlt_ToDoTask)
    #                                         .filter(MdlIlt_ToDoTask.meeting_response_id == meetingResponseId,
    #                                                 MdlIlt_ToDoTask.id == data.todoList[i].id)
    #                                         .one())
    #                     user_todo_record.description = data.todoList[i].description
    #                     user_todo_record.due_date = data.todoList[i].dueDate
    #                     user_todo_record.status = data.todoList[i].status
    #                     db.commit()
    #                     db.refresh(user_todo_record)

    #             if data.issues:
    #                 for i in range(len(data.updates)):
    #                     if not data.issues[i].issueid:
    #                         continue
    #                     issue_map_re = (db.query(MdlIltissue)
    #                                     .filter(MdlIltissue.meeting_response_id == meetingResponseId,
    #                                             MdlIltissue.issue_id == data.issues[i].issueid)
    #                                     .one())
    #                     user_issue_record = (db.query(Mdl_issue)
    #                                          .filter(Mdl_issue.id == issue_map_re.issue_id).one())

    #                     user_issue_record.id = data.issues[i].issueid
    #                     user_issue_record.issue = data.issues[i].issue
    #                     user_issue_record.priority = data.issues[i].priorityId
    #                     user_issue_record.created_at = datetime.utcnow()
    #                     user_issue_record.due_date = data.issues[i].created_at
    #                     user_issue_record.resolves_flag = data.issues[i].resolvedFlag
    #                     user_issue_record.recognize_performance_flag = data.issues[
    #                         i].recognizePerformanceFlag
    #                     user_issue_record.teacher_support_flag = data.issues[i].teacherSupportFlag
    #                     user_issue_record.leader_support_flag = data.issues[i].leaderSupportFlag
    #                     user_issue_record.advance_equality_flag = data.issues[i].advanceEquityFlag
    #                     user_issue_record.others_flag = data.issues[i].othersFlag
    #                     db.commit()
    #                     db.refresh(user_issue_record)

    #         except Exception as e:
    #             raise CustomException(
    #                 404,  f"all details with corresponding meeting responceId is not found, error - {str(e)}")

    #         return {

    #             "statusCode": 200,
    #             "userMessage": "we have successfully added all records"
    #         }
    #     except Exception as e:
    #         raise CustomException(500,  f"Internal Server Error = {str(e)}")

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
        meeting_id,  = db.query(MdlIltMeetingResponses.meeting_id).filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId).one()
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one_or_none()
        if meeting_re.start_at and meeting_re.end_at is None:
            iltId, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id==meeting_id).one_or_none()
            ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==iltId).one_or_none()
            if user_id != meeting_re.note_taker_id and user_id != ownerId:
                raise CustomException(404,  "Only Ilt owner and Note Taker can edit the data.")
        if meeting_re.end_at:
            raise CustomException(404,  "This meeting has been end, We can not update it.")

        if name:
            user_meetingResponse_record.rockName = name
        if onTrack != True:
            onTrack = False
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

        meeting_id,  = db.query(MdlIltMeetingResponses.meeting_id).filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId).one()
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one_or_none()
        if meeting_re.start_at and meeting_re.end_at is None:
            iltId, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id==meeting_id).one_or_none()
            ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==iltId).one_or_none()
            if user_id != meeting_re.note_taker_id and user_id != ownerId:
                raise CustomException(404,  "Only Ilt owner and Note Taker can edit the data.")
        if meeting_re.end_at:
            raise CustomException(404,  "This meeting has been end, We can not update it.")
        
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
        meeting_id,  = db.query(MdlIltMeetingResponses.meeting_id).filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId).one()
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one_or_none()
        

        if meeting_re.start_at and meeting_re.end_at is None:
            iltId, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id == meeting_id).one_or_none()
            ilt_re = db.query(MdlIlts).filter(MdlIlts.id==iltId).one_or_none()
            current_member_ids = [mid for mid, in db.query(MdlIltMembers.member_id).filter(MdlIltMembers.ilt_id == iltId).all()]
            mr_user_id, = db.query(MdlIltMeetingResponses.meeting_user_id).filter(
                MdlIltMeetingResponses.meeting_response_id==meetingResponseId).one_or_none()
            
            if user_id not in current_member_ids:
                raise CustomException(404,  "Cannot edit, Member is not in current ILT.")
            if user_id != mr_user_id or user_id != ilt_re.owner_id or user_id != meeting_re.note_taker_id :
                raise CustomException(404,  "Cannot edit, Invalid member.")
        
        if meeting_re.start_at is None:
            raise CustomException(500,  "Meeting is not started.")
            
        if meeting_re.end_at:
            raise CustomException(404,  "This meeting has been end, We can not update it.")
            
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
