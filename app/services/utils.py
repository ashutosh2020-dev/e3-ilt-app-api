
from app.models import MdlMeetings, MdlIltMeetings, MdlIltMeetingResponses, MdlIltissue, \
    MdlMeetingsResponse, Mdl_issue, MdlIlt_ToDoTask, MdlUsers
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from app.exceptions.customException import CustomException



def get_upcomming_meeting(ilt_id, db):

    return [i for i, in db.query(MdlMeetings.id,)
                            .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                            .filter(MdlIltMeetings.ilt_id == ilt_id)
                            .filter(MdlMeetings.end_at == None)
                            .all()
                            ]

def get_completed_issue_todo_list(meeting_id, db, user_id=None):
    ## check pending- issue, todo, 
    sub_query = (db.query(MdlIltMeetingResponses.meeting_response_id)
                        .filter(MdlIltMeetingResponses.meeting_id==meeting_id, 
                                MdlIltMeetingResponses.is_active==True))
    if user_id:
        sub_query = sub_query.filter(MdlIltMeetingResponses.meeting_user_id==user_id)
    sub_query = sub_query.all()
    member_meeting_response_id_list = [meeting_response_id
                                        for meeting_response_id, in sub_query]
    member_meeting_responce_records = [db.query(MdlMeetingsResponse)
                                            .filter(MdlMeetingsResponse.id==m_r_id).one()
                                            for m_r_id in member_meeting_response_id_list]
    issue_record_list = []
    to_do_record_list = []
    for responceRecord in member_meeting_responce_records:
        meeting_response_id = responceRecord.id
        ##issue
        issue_record_list.extend([id for id, in db.query(Mdl_issue.id)
                                    .join(MdlIltissue, Mdl_issue.id==MdlIltissue.issue_id )
                                    .filter(and_((MdlIltissue.meeting_response_id==meeting_response_id) 
                                            , (MdlIltissue.is_active == True )
                                            , or_(Mdl_issue.resolves_flag==True, Mdl_issue.priority == 4)))
                                    .all()
                                    ])
        ##ToDo
        to_do_record_list.extend([p_todo_id for p_todo_id, in db.query(MdlIlt_ToDoTask.id)
                                    .filter(and_(MdlIlt_ToDoTask.meeting_response_id==meeting_response_id,
                                                    MdlIlt_ToDoTask.status == True, 
                                                    MdlIlt_ToDoTask.is_active==True))
                                    .all()])        
    return issue_record_list, to_do_record_list

def inactivate_all_completed_issue_todo_list(listOfIssueIds, listOfToDoIds, 
                                             ilt_id, db:Session):

    upcomming_meeting_ids = get_upcomming_meeting(ilt_id, db)
        
    for id in listOfIssueIds:
        map_re = (db.query(MdlIltissue).filter(MdlIltissue.issue_id==id, 
                                            MdlIltissue.is_active==True)
                .order_by(MdlIltissue.id.desc())
                .first())        
        parent_responce_id= map_re.meeting_response_id 
        parent_user_id, = (db.query(MdlIltMeetingResponses.meeting_user_id)
                        .filter(MdlIltMeetingResponses.meeting_response_id==parent_responce_id)
                        .one_or_none()
                        )
        
        list_of_user_meetingResponce = [db.query(MdlIltMeetingResponses.meeting_response_id,)
                                        .filter(MdlIltMeetingResponses.meeting_id == mid,
                                                MdlIltMeetingResponses.meeting_user_id == parent_user_id)
                                        .one()[0] for mid in upcomming_meeting_ids
                                        ]
        for upcoming_meetingResponce in list_of_user_meetingResponce:
            db_issue =  (db.query(MdlIltissue)
                            .filter(MdlIltissue.issue_id == id, 
                                    MdlIltissue.meeting_response_id == upcoming_meetingResponce,
                                    MdlIltissue.is_active==True)
                            .one_or_none())
            if db_issue:
                db_issue.is_active = False
                db.add(db_issue)
        db.commit()

    for todoid in listOfToDoIds:
            parent_todo_record = (db.query(MdlIlt_ToDoTask)
                                    .filter(MdlIlt_ToDoTask.id == todoid,
                                            MdlIlt_ToDoTask.is_active == True)
                                    .one_or_none())
            if parent_todo_record is None:
                    raise CustomException(400,  "records is not available")
            
            parent_to_do_id = parent_todo_record.parent_to_do_id if parent_todo_record.parent_to_do_id else parent_todo_record.id
            
            parent_user_id, = (db.query(MdlIltMeetingResponses.meeting_user_id)
                                .filter(MdlIltMeetingResponses.meeting_response_id == parent_todo_record.meeting_response_id)
                                .one_or_none()
                            )
            list_of_user_meetingResponce = [db.query(MdlIltMeetingResponses.meeting_response_id,)
                                            .filter(MdlIltMeetingResponses.meeting_id == mid,
                                                    MdlIltMeetingResponses.meeting_user_id == parent_user_id)
                                            .one()[0] for mid in upcomming_meeting_ids
                                            ]
            for upcoming_meetingResponce in list_of_user_meetingResponce:
                db_todo = (db.query(MdlIlt_ToDoTask)
                                            .filter(and_(MdlIlt_ToDoTask.parent_to_do_id == parent_to_do_id,
                                                    MdlIlt_ToDoTask.meeting_response_id == upcoming_meetingResponce,
                                                    MdlIlt_ToDoTask.is_active == True))
                                            .one_or_none())
                if db_todo:
                    db_todo.is_active = False
                    db.add(db_todo)
            db.commit()

def replacing_ownership_of_issue_todo_for(associated_responceId_list, default_owner_responceId_list, db:Session):
    
    for responce_id, defult_responce_id in zip(associated_responceId_list, default_owner_responceId_list):
        get_all_issue_re = (db.query(MdlIltissue)
                                .filter(and_(MdlIltissue.meeting_response_id==responce_id,
                                        MdlIltissue.is_active==True))
                                .all())
        for db_re in get_all_issue_re: 
                db_re.meeting_response_id = defult_responce_id
                if db_re.parent_meeting_responce_id ==responce_id:
                    db_re.parent_meeting_responce_id = defult_responce_id
                db.add(db_re)
        db.commit()
                
        get_all_todo_id = (db.query(MdlIlt_ToDoTask)
                           .filter(MdlIlt_ToDoTask.meeting_response_id == responce_id,
                                   MdlIlt_ToDoTask.is_active==True).all()
                                )
        for db_re in get_all_todo_id:
                db_re.meeting_response_id = defult_responce_id
                db.add(db_re)
        db.commit()
    pass

def get_user_info(db, userId=None, responceId=None):
    if responceId:
        userId, = db.query(MdlIltMeetingResponses.meeting_user_id).filter(MdlIltMeetingResponses.meeting_response_id==responceId,
                                                MdlIltMeetingResponses.is_active==True).one_or_none()
    record = db.query(MdlUsers).filter(MdlUsers.id == userId).one()
    return {
                "userId": record.id,
                "firstName": record.fname,
                "lastName": record.lname
        }
