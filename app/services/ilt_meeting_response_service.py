from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from app.models import MdlIlt_ToDoTask, Mdl_updates, \
    MdlMeetingsResponse, MdlIltMeetingResponses, MdlRocks, \
    Mdl_issue, MdlUsers, MdlIltissue, MdlMeetings, MdlIlts, \
    MdlRocks_members, MdlIltMembers, MdlIltMeetings, MdlPriorities, MdlIlt_ToDoTask_map
from sqlalchemy import desc, join
from typing import List, Optional
from app.schemas.meeting_response import MeetingResponse, Duedate, RockInput, RockOutput, Member
from datetime import datetime, timezone
from typing import Annotated, Union
from app.exceptions.customException import CustomException
from app.services.utils import get_user_info

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
            .filter(MdlIltMeetingResponses.meeting_response_id == meetingResponseId,
                     MdlIltMeetingResponses.is_active==True).one()
        ilt_meet_id = ilt_meet_re.meeting_id
        user_meetingResponse_record = db.query(MdlMeetingsResponse)\
            .filter(MdlMeetingsResponse.id == meetingResponseId).one_or_none()
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
                "status": record.status,
                "isRepeat": True if (db.query(MdlIlt_ToDoTask)
                                     .filter(MdlIlt_ToDoTask.parent_to_do_id == record.id)
                                     .count() >= 1) else False,
                "todoOwner": get_user_info(responceId=record.meeting_response_id, db=db),
                "todoMemebers": [get_user_info(userId=map_re.user_id, db=db)
                                    for map_re in  db.query(MdlIlt_ToDoTask_map)
                                     .filter(MdlIlt_ToDoTask_map.parent_to_do_id == (record.parent_to_do_id 
                                                        if record.parent_to_do_id else record.id)
                                            , MdlIlt_ToDoTask_map.is_todo_member==True)
                                     .all()]
            } for record in db.query(MdlIlt_ToDoTask)
            .filter(MdlIlt_ToDoTask.meeting_response_id == meetingResponseId,
                    MdlIlt_ToDoTask.is_active==True).all()]

        issue_record = (db.query(MdlIltissue)
                            .filter(MdlIltissue.meeting_response_id == meetingResponseId, 
                                    MdlIltissue.is_active==True)
                            .all())

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
            "updates": user_update_record,
            "todoList": user_todolist_record,
            "issues": iltMeetingResponse_issues
        }

    def create_meeting_responses_empty_for_ILTmember(self, meeting_id: int, member_list: list, iltId: int, db: Session):
        try:
            for uid in member_list:
                db_meeting_response = MdlMeetingsResponse(attendance_flag=False, checkin_personal_best=None,
                                                          checkin_professional_best=None, rating=None,
                                                          feedback=None, notes=None)
                db.add(db_meeting_response)
                db.commit()
                db.refresh(db_meeting_response)
                map_record = MdlIltMeetingResponses(meeting_id=meeting_id,
                                                    meeting_response_id=db_meeting_response.id, 
                                                    meeting_user_id=uid,
                                                    is_active=True)
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
                    check_responce_re = (db.query(MdlIltMeetingResponses).filter(MdlIltMeetingResponses.meeting_id==mid,
                                                            MdlIltMeetingResponses.meeting_user_id ==uid)
                                                    .one_or_none())
                    if check_responce_re is not None:
                        check_responce_re.is_active = True
                        db.add(check_responce_re)
                        db.commit()
                        db.refresh(check_responce_re)
                    else:
                        db_meeting_response = MdlMeetingsResponse(attendance_flag=None,
                                                                checkin_personal_best=None, checkin_professional_best=None,
                                                                rating=None, feedback=None, notes=None)
                        db.add(db_meeting_response)
                        db.commit()
                        db.refresh(db_meeting_response)
                        map_record = MdlIltMeetingResponses(meeting_id=mid,
                                                            meeting_response_id=db_meeting_response.id, 
                                                            meeting_user_id=uid,
                                                            is_active=True)
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
                                                  rating=ratings, feedback=feedback, notes=notes)
        db.add(db_metting_response)
        db.commit()
        db.refresh(db_metting_response)
        map_record = MdlIltMeetingResponses(
            meeting_id=meeting_id, meeting_response_id=db_metting_response.id, is_active=True)
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
                                                   ,MdlRocks.created_at <= meeting_re.schedule_start_at
                                                   )
                                    .all())
        meeting_rock_records = []
        for record in list_rocks_re:  
            meeting_date = meeting_re.end_at if meeting_re.end_at else meeting_re.schedule_start_at
            rockObj = RockOutput()
            rockObj.rockId =record.id
            rockObj.iltId = record.ilt_id
            rockObj.name = record.name
            rockObj.description = record.description
            rockObj.onTrack = record.on_track_flag
            if record.is_complete:
                rockObj.isComplete = False if  record.completed_at > meeting_date else True
            else:
                rockObj.isComplete = False
            rockObj.completeAt = record.completed_at if record.is_complete else None

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
        if db.query(MdlIltMembers).filter(and_(MdlIltMembers.ilt_id==rockData.iltId,
                                               MdlIltMembers.member_id == rockData.rockOwnerId,
                                               MdlIltMembers.is_active==True)
                                          ).one_or_none() is None:
            raise CustomException(400,  "Rock owner not found.")
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id ==meeting_id).one_or_none()
        if meeting_re is None:
             raise CustomException(400,  "Meeting not found.")
        user_re = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        if user_re is None:
            raise CustomException(404,  "User not found")
        ilt_re = db.query(MdlIlts).filter(MdlIlts.id==rockData.iltId).one_or_none()
        if ilt_re is None:
            raise CustomException(404,  "Ilt not found")
        #verify each member
        rockMembers = rockData.rockMembers
        rockMembers.append(rockData.rockOwnerId)
        unique_user_ids = list(set(rockMembers))

        ilt_member_count = (db.query(MdlIltMembers)
                            .filter(MdlIltMembers.ilt_id == rockData.iltId, MdlIltMembers.member_id.in_(unique_user_ids),
                                    MdlIltMembers.is_active==True)
                            .count())
        if ilt_member_count != len(unique_user_ids):
            raise CustomException(
                404, "Record not found for some users. They are not members of the ILT")
        rock_name = rockData.name.strip().lower()
        check_title = (db.query(MdlRocks).filter(and_(MdlRocks.ilt_id == rockData.iltId,
                                                      func.lower(MdlRocks.name) == rock_name))
                       .first())
        if rockData.rockId:
            if rockData.isComplete:
                if rockData.completeAt:
                    if  rockData.completeAt > datetime.utcnow(): 
                        raise CustomException(404, "Date and time should be greater than current time!")
                    
            #update
            rock_id = rockData.rockId
            db_rock = db.query(MdlRocks).filter(and_(MdlRocks.id==rock_id, MdlRocks.ilt_id==rockData.iltId)).one_or_none()
            db_current_owner = (db.query(MdlRocks_members)
                                .filter(and_(MdlRocks_members.ilt_rock_id==rock_id,
                                        MdlRocks_members.is_rock_owner==True))
                                .one_or_none())
            
            if user_id not in [ilt_re.owner_id, meeting_re.note_taker_id] and user_id != db_current_owner.user_id:
                raise CustomException(404, "User is not allowed to update the rock")
            if user_id == db_current_owner.user_id and user_id != ilt_re.owner_id and user_id != meeting_re.note_taker_id:
                if db_rock.name != rockData.name or db_rock.is_complete!=rockData.isComplete or db_rock.description != rockData.description:
                    raise CustomException(404, "User can update only rock status.")

            if db_rock.name.lower() !=rockData.name.strip().lower(): 
                if check_title:
                    raise CustomException(404, "Rock Already Exists, Please change Rock Name")
            
            db_rock.name = rockData.name.strip()
            db_rock.description = rockData.description
            db_rock.is_complete = rockData.isComplete
            db_rock.updated_at = datetime.utcnow()
            db_rock.on_track_flag = rockData.onTrack
            if rockData.isComplete and rockData.isComplete:
                db_rock.completed_at = rockData.completeAt
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

            if rockData.rockOwnerId != db_current_owner.user_id:
                db_current_owner.is_rock_owner = False 
                db_current_owner.is_rock_member = False 
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
                if user_id == db_current_owner.user_id and user_id != ilt_re.owner_id and user_id != meeting_re.note_taker_id:
                    if len(new_user) != 0 or len(remove_user) != 0 or rockData.rockOwnerId != db_current_owner.user_id:
                        raise CustomException(500,"This user not allowed to update rock") 
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
        
        if user_id not in [ilt_re.owner_id, meeting_re.note_taker_id]:
            raise CustomException(404, "User not allowed to create rock")

        # create
        db_rock = MdlRocks(ilt_id=rockData.iltId, 
                           name=rock_name, 
                           description=rockData.description, 
                           is_complete =False,
                           created_at = meeting_re.schedule_start_at,
                           on_track_flag = rockData.onTrack,
                           completed_at=datetime(1, 1, 1, 0, 0, 0))
        
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
        

        return {
            "statusCode": 200,
            "userMessage": "Rock added"
        }


    def create_update_to_do_list(self, user_id: int, id: int, meetingResponseId: int, description: str,
                                 dueDate: Duedate, status: bool, toDoMemeberIds:List, db: Session):
        user_re = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        if user_re is None:
            raise CustomException(400,  f" userId is not valid")
        if db.query(MdlMeetingsResponse).filter(MdlMeetingsResponse.id == meetingResponseId).one_or_none() is None:
            raise CustomException(400,  f" meetingResponseId is not valid")
        if toDoMemeberIds:
            if db.query(MdlUsers.id).filter(MdlUsers.id.in_(toDoMemeberIds)).count() != len(toDoMemeberIds):
                raise CustomException(404, "invalid members list!")
        meeting_id,  = (db.query(MdlIltMeetingResponses.meeting_id)
                        .filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId,
                                MdlIltMeetingResponses.is_active==True)
                        .one())
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one_or_none()
        if meeting_re.start_at:# and meeting_re.end_at is None:
            iltId, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id==meeting_id).one_or_none()
            ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==iltId).one_or_none()
            if user_id != meeting_re.note_taker_id and user_id != ownerId and user_re.role_id != 4 :
                 raise CustomException(404,  "Only Ilt owner, Note Taker and Director can edit the data.")
        # if meeting_re.end_at:
        #     raise CustomException(404,  "This meeting has been end, We can not update it.")
        if id > 0:
            user_todo_record = (db.query(MdlIlt_ToDoTask)
                                .filter(MdlIlt_ToDoTask.id == id,
                                        MdlIlt_ToDoTask.is_active==True)
                                .one())
            user_todo_record.description = description
            user_todo_record.due_date = dueDate
            user_todo_record.status = status
            db.commit()
            db.refresh(user_todo_record)
            # update member ids
            if toDoMemeberIds:
                toDoMemeberIds = set(toDoMemeberIds)
                parent_to_do_id = (user_todo_record.parent_to_do_id if user_todo_record.parent_to_do_id 
                                    else user_todo_record.id)
                
                active_todo_memberIds = set([uid for uid, in db.query(MdlIlt_ToDoTask_map.user_id)
                                              .filter(MdlIlt_ToDoTask_map.parent_to_do_id == parent_to_do_id,
                                                      MdlIlt_ToDoTask_map.is_todo_member==True).all()])
                inactive_todo_memberIds = set([uid for uid, in db.query(MdlIlt_ToDoTask_map.user_id)
                                         .filter(MdlIlt_ToDoTask_map.parent_to_do_id == parent_to_do_id,
                                                 MdlIlt_ToDoTask_map.is_todo_member == False).all()])
                all_todo_memberIds = active_todo_memberIds | inactive_todo_memberIds
                removed_members = active_todo_memberIds - toDoMemeberIds
                new_member = toDoMemeberIds - set(all_todo_memberIds)
                activate_inactive_members = toDoMemeberIds & inactive_todo_memberIds

                # create new_todo_member
                db_new_todo_member_re = [MdlIlt_ToDoTask_map(parent_to_do_id = parent_to_do_id,
                                                             user_id = m_id,
                                                             is_todo_member = True) for m_id in new_member]
                db.add_all(db_new_todo_member_re)
                db.commit()
                #activate already existing member
                for m_id in activate_inactive_members:
                    print(m_id, "----",new_member)
                    db_inactive_member = (db.query(MdlIlt_ToDoTask_map)
                                          .filter(MdlIlt_ToDoTask_map.parent_to_do_id == parent_to_do_id,
                                                  MdlIlt_ToDoTask_map.user_id==m_id
                                                  )
                                          .one_or_none())
                    if db_inactive_member is not None:
                        db_inactive_member.is_todo_member = True
                    db.add(db_inactive_member)
                    db.commit()
                    db.refresh(db_inactive_member)
                # inactivate
                for m_id in removed_members:
                    db_removed_member = (db.query(MdlIlt_ToDoTask_map)
                                          .filter(MdlIlt_ToDoTask_map.parent_to_do_id == parent_to_do_id,
                                                  MdlIlt_ToDoTask_map.user_id==m_id
                                                  )
                                          .one_or_none())
                    if db_removed_member is not None:
                        db_removed_member.is_todo_member = False
                        db.add(db_removed_member)
                    db.commit()
                    db.refresh(db_removed_member)

        else:
            # create toDO records with all memebers 
            db_meeting_todo = MdlIlt_ToDoTask(
                meeting_response_id=meetingResponseId, description=description, due_date=dueDate, status=status, 
                created_at= datetime.utcnow(), is_active = True)
            db.add(db_meeting_todo)
            db.commit()
            db.refresh(db_meeting_todo)
            create_by_uid, = (db.query(MdlIltMeetingResponses.meeting_user_id)
                                .filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId)
                                .one_or_none())
            if create_by_uid not in toDoMemeberIds:
                toDoMemeberIds.append(create_by_uid)
            
            db_todo_member_re = [MdlIlt_ToDoTask_map(parent_to_do_id = db_meeting_todo.id,
                                 user_id = uid, 
                                 is_todo_member=True) for uid in toDoMemeberIds]
            db.add_all(db_todo_member_re)
            db.commit()

        meeting_ResponseId_list = [id for id, in db.query(MdlIltMeetingResponses.meeting_response_id)
                                                .filter(MdlIltMeetingResponses.meeting_id==meeting_id,
                                                        MdlIltMeetingResponses.is_active == True).all()]
        user_todolist_record = [
            {
                "todoListId": record.id,
                "description": record.description,
                "dueDate": record.due_date,
                "status": record.status,
                "isRepeat": True if (db.query(MdlIlt_ToDoTask)
                                    .filter(MdlIlt_ToDoTask.parent_to_do_id==record.id)
                                    .count()>=1) else False,
                "todoOwner": get_user_info(responceId=record.meeting_response_id, db=db),
                "todoMemebers": [get_user_info(userId=map_re.user_id, db=db)
                                    for map_re in  db.query(MdlIlt_ToDoTask_map)
                                     .filter(MdlIlt_ToDoTask_map.parent_to_do_id == (record.parent_to_do_id 
                                                        if record.parent_to_do_id else record.id)
                                                        , MdlIlt_ToDoTask_map.is_todo_member==True)
                                     .all()]
            } for record in db.query(MdlIlt_ToDoTask)
            .filter(MdlIlt_ToDoTask.meeting_response_id.in_(meeting_ResponseId_list),
                    MdlIlt_ToDoTask.is_active==True).all()]

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
            meeting_id,  = (db.query(MdlIltMeetingResponses.meeting_id)
                            .filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId,
                                    MdlIltMeetingResponses.is_active==True)
                            .one())
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
                                                                                   MdlIltMeetingResponses.meeting_response_id==assign_to_responce_id,
                                                                                   MdlIltMeetingResponses.is_active==True)).one_or_none()
        if check_assign_to_responce_id is None:
            raise CustomException(404,  "This responce_id is noo longer associated with This Meeting.")
        
        meeting_id_,  = (db.query(MdlIltMeetingResponses.meeting_id)
                        .filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId,
                                MdlIltMeetingResponses.is_active==True)
                        .one())
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
                                            .filter(MdlIltMeetingResponses.meeting_id == meeting_id,
                                                    MdlIltMeetingResponses.is_active==True)
                                            .all()]
                db_issue_latest_re = (db.query(MdlIltissue)
                                      .filter(and_(MdlIltissue.issue_id == id,
                                                   MdlIltissue.meeting_response_id.in_(meeting_responcesId_list),
                                                   MdlIltissue.is_active==True))
                                        .one_or_none())
                if db_issue_latest_re.meeting_response_id != assign_to_responce_id:
                    if db_issue_latest_re.meeting_response_id == db_issue_latest_re.parent_meeting_responce_id:
                        db_issue_latest_re.meeting_response_id = assign_to_responce_id
                        db_issue_latest_re.parent_meeting_responce_id = assign_to_responce_id
                    else:
                        db_issue_latest_re.meeting_response_id = assign_to_responce_id
                    db.commit()
                    db.refresh(db_issue_latest_re)

            issue_map_re = (db.query(MdlIltissue)
                            .filter(and_(MdlIltissue.meeting_response_id == db_issue_latest_re.meeting_response_id,
                                    MdlIltissue.issue_id == id, 
                                    MdlIltissue.is_active==True))
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
                meeting_response_id=assign_to_responce_id, issue_id=db_issue.id, 
                parent_meeting_responce_id=assign_to_responce_id,
                is_active=True)
            db.add(db_meeting_issue)
            db.commit()
            db.refresh(db_meeting_issue)

        issue_records = (db.query(MdlIltissue)
                            .filter(MdlIltissue.meeting_response_id == responce_id.id,
                                    MdlIltissue.is_active==True)
                            .order_by(MdlIltissue.id.desc())
                            .all())

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
            "userMessage": "Issue have been modified successfully" if id else "Issue have been created successfully",
            "data": issues_records
        }


    # def update_meetingResponce_rocks(self, user_id: int,
    #                                  meetingResponseId: int,
    #                                  name: str,
    #                                  onTrack: bool,
    #                                  db: Session):
    #     if db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none() is None:
    #         raise CustomException(400,  f"invaild users")

    #     user_meetingResponse_record = (db.query(MdlMeetingsResponse)
    #                                    .filter(MdlMeetingsResponse.id == meetingResponseId)
    #                                    .one_or_none())
    #     if user_meetingResponse_record is None:
    #         raise CustomException(404,  "MeetingsResponse record did not found")
    #     meeting_id,  = (db.query(MdlIltMeetingResponses.meeting_id)
    #                     .filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId,
    #                             MdlIltMeetingResponses.is_active==True)
    #                     .one())
    #     meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one_or_none()
    #     if meeting_re.start_at and meeting_re.end_at is None:
    #         iltId, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id==meeting_id).one_or_none()
    #         ownerId, = db.query(MdlIlts.owner_id).filter(MdlIlts.id==iltId).one_or_none()
    #         if user_id != meeting_re.note_taker_id and user_id != ownerId:
    #             raise CustomException(404,  "Only Ilt owner and Note Taker can edit the data.")
    #     if meeting_re.end_at:
    #         raise CustomException(404,  "This meeting has been end, We can not update it.")

    #     if name:
    #         user_meetingResponse_record.rockName = name
    #     if onTrack != True:
    #         onTrack = False
    #     user_meetingResponse_record.onTrack = onTrack

    #     db.commit()
    #     db.refresh(user_meetingResponse_record)

    #     return {
    #         "statusCode": 200,
    #         "userMessage": "Rock Updated successfully"
    #     }

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

        meeting_id,  = (db.query(MdlIltMeetingResponses.meeting_id)
                        .filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId,
                                MdlIltMeetingResponses.is_active==True)
                        .one())
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
        meeting_id,  = (db.query(MdlIltMeetingResponses.meeting_id)
                        .filter(MdlIltMeetingResponses.meeting_response_id==meetingResponseId,
                                MdlIltMeetingResponses.is_active==True)
                        .one())
        meeting_re = db.query(MdlMeetings).filter(MdlMeetings.id==meeting_id).one_or_none()
        

        if meeting_re.start_at and meeting_re.end_at is None:
            iltId, = db.query(MdlIltMeetings.ilt_id).filter(MdlIltMeetings.ilt_meeting_id == meeting_id).one_or_none()
            ilt_re = db.query(MdlIlts).filter(MdlIlts.id==iltId).one_or_none()
            current_member_ids = [mid for mid, in db.query(MdlIltMembers.member_id).filter(MdlIltMembers.ilt_id == iltId,
                                                                                           MdlIltMembers.is_active==True).all()]
            mr_user_id, = db.query(MdlIltMeetingResponses.meeting_user_id).filter(
                MdlIltMeetingResponses.meeting_response_id==meetingResponseId,
                MdlIltMeetingResponses.is_active==True).one_or_none()
            
            if user_id not in current_member_ids:
                raise CustomException(404,  "Cannot edit, Member is not in current ILT.")
            if user_id not in [mr_user_id, ilt_re.owner_id , meeting_re.note_taker_id] :
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
