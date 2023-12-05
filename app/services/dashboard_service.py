from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from app.models import MdlUsers, MdlIltMeetings, MdlMeetings,\
    MdlIltMembers, MdlIltMeetingResponses, MdlMeetingsResponse, MdlIltissue,\
    Mdl_issue, MdlIlt_ToDoTask, MdlIlts, MdlSchools, MdlDistrictMember, MdlDistrict, MdlRocks
from app.schemas.dashboard_schemas import SummaryData, PercentageData, DashboardFilterParamaters, TimeFilterParameter
from datetime import datetime, timezone
from app.exceptions.customException import CustomException
"""
meetings wrt to ilt which has finished
meeting_responce_list for all user wrt each meeting in that ilt

compute attendance, rock on-track, average rating, issue,
formula - total present/total user for all meetings, 
		on_track/num_of_tracks for all meetings,
		avg rating for single meeting then compute for all, 

"""


def calculate_meeting_status(schedule_start_at, start_at, end_at):
    current_datetime = datetime.now()
    if current_datetime < schedule_start_at and start_at == 0:
        return 0  # notStarted
    elif current_datetime > schedule_start_at and start_at == 0:
        return 0  # skipped
    elif current_datetime >= start_at and end_at == 0:
        return 1  # inProgress
    else:
        return 2  # completed

def compute_meetings_avg():
    pass
def get_associated_schoolId_wrt_role(user_id:int, role_id:int, FilterParamaters:DashboardFilterParamaters, db:Session):
        user_id_list = [user_id,]
        list_ilts = []
        list_of_school_id = []

        if FilterParamaters.distictId or FilterParamaters.schoolId:
            if role_id<4:
                raise CustomException(404,  "Only Director is allowed to see filter info.")
            if  FilterParamaters.districtAggregateFlag ==True:
                if FilterParamaters.distictId:
                    for d_id in FilterParamaters.distictId:
                        list_of_school_in_d_id = [id for id, in db.query(MdlSchools.id)
                                                    .filter(MdlSchools.district==d_id)
                                                    .distinct()
                                                    ]
                        list_of_school_id.append(list_of_school_in_d_id)

                        
                if FilterParamaters.schoolId:
                    raise CustomException(404,  "School ids are not allowed if districtAggregateFlag is True")
            else:
                if FilterParamaters.distictId:
                    schools_ids = [[id] for id, in db.query(MdlSchools.id)
                                                    .filter(MdlSchools.district.in_(FilterParamaters.distictId))
                                                    .distinct()
                                                    ]
                    list_of_school_id.extend(schools_ids)

                if FilterParamaters.schoolId:
                    list_of_school_id.extend([[i] for i in FilterParamaters.schoolId])

            return list_of_school_id

        # for ilt
        if role_id==3:
            # extend child facilitator
            user_id_list.extend([id
                                 for id, in db.query(MdlUsers.id).filter(MdlUsers.parent_user_id == user_id).all()])
            # remove duplicates
            user_id_list = list(set(user_id_list))
            # get all ilt where user_id is member
            list_ilts.extend([record.ilt_id for record in db.query(
                                            MdlIltMembers).filter(MdlIltMembers.member_id == user_id, 
                                                                  MdlIltMembers.is_active==True).all()])
            for  uid in user_id_list:
                list_ilts.extend([record.id for record in db.query(
                    MdlIlts).filter(MdlIlts.owner_id == uid).all()])
            unique_school_ids = [[id] for id, in db.query(MdlIlts.school_id)
                                 .filter(MdlIlts.id.in_(list_ilts))
                                 .distinct()
                                 ]
            list_of_school_id.extend(unique_school_ids)

        elif role_id==4:
            if  FilterParamaters.districtAggregateFlag ==True:
                district_ids = [district_id for district_id, in db.query(MdlDistrictMember.district_id).filter(MdlDistrictMember.user_id==user_id).distinct()]
                for d_id in district_ids:
                        list_of_school_in_d_id = [id for id, in db.query(MdlSchools.id)
                                                    .filter(MdlSchools.district==d_id)
                                                    .distinct()
                                                    ]
                        list_of_school_id.append(list_of_school_in_d_id)

            else:
                district_ids = [district_id for district_id, in db.query(MdlDistrictMember.district_id).filter(MdlDistrictMember.user_id==user_id).all()]            
                unique_school_ids = [[id] for id, in db.query(MdlSchools.id).filter(MdlSchools.district.in_(district_ids)).distinct()]
                list_of_school_id.extend(unique_school_ids)

        return list_of_school_id

def get_rock_aggegrates(list_of_ilt, db:Session):
    
    ontrack_count = db.query(MdlRocks).filter(MdlRocks.ilt_id.in_(list_of_ilt), 
                                              MdlRocks.on_track_flag ==True,
                                              MdlRocks.is_complete == False).count()
    offtrack_count = db.query(MdlRocks).filter(MdlRocks.ilt_id.in_(list_of_ilt), 
                                               MdlRocks.on_track_flag ==False,
                                               MdlRocks.is_complete == False).count()
    # total_rocks = db.query(MdlRocks).filter(MdlRocks.ilt_id.in_(list_of_ilt)).count()    
    total = ontrack_count+offtrack_count
    return PercentageData(percentage=round((ontrack_count/total)*100, 1) if total !=0 else 0,
                          total=total
                          )
def get_rock_aggegrates_for_meeting(ilt_id, meeting_id, db:Session):
    meeting_schedule_start_at, = db.query(MdlMeetings.schedule_start_at).filter(
        MdlMeetings.id == meeting_id).one_or_none()

    ontrack_count = (db.query(MdlRocks)
                   .filter(and_(MdlRocks.ilt_id == ilt_id,
                           MdlRocks.created_at <= meeting_schedule_start_at,
                           MdlRocks.on_track_flag ==True, 
                           MdlRocks.is_complete ==False))
                   .count())
    offtrack_count = (db.query(MdlRocks)
                   .filter(and_(MdlRocks.ilt_id == ilt_id,
                           MdlRocks.created_at <= meeting_schedule_start_at,
                           MdlRocks.on_track_flag ==False, 
                           MdlRocks.is_complete ==False))
                   .count())
    total = ontrack_count + offtrack_count
    return PercentageData(percentage=round((ontrack_count/total)*100, 1) if total != 0 else 0,
                          total=total)

class DashboardService:
    def get_ilt_Meetings_dashboard_info(self, user_id: int, FilterParamaters:TimeFilterParameter, ilt_id: int, db: Session):
        # check user
        user_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if user_record is None:
            raise CustomException(404,  "User not found")
        num_of_ended_meeting = 0
        num_of_notStarted_meeting = 0
        num_of_inprogress_meeting = 0
        num_of_member_in_ilt = 0
        start_date = FilterParamaters.startDate
        end_date = FilterParamaters.endDate

        list_of_ended_meeting_ids = []
        list_of_meeting_obj = []
        if user_record.role_id <= 4:
            list_meeting_subquery = (db.query(MdlMeetings)
                                    .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                    .filter(MdlIltMeetings.ilt_id == ilt_id))
            if start_date and end_date:
                    list_meeting_subquery = list_meeting_subquery.filter(and_(MdlMeetings.schedule_start_at>start_date,
                                            MdlMeetings.schedule_start_at<end_date))
            list_meeting_records = list_meeting_subquery.order_by(MdlMeetings.schedule_start_at.asc()).all()
                                
            
            if list_meeting_records:
                for meeting_record in list_meeting_records:
                    status = calculate_meeting_status(
                        schedule_start_at=meeting_record.schedule_start_at,
                        start_at=meeting_record.start_at if meeting_record.start_at else 0,
                        end_at=meeting_record.end_at if meeting_record.end_at else 0)
                    if status == 2:
                        num_of_ended_meeting += 1
                        list_of_ended_meeting_ids.append(meeting_record.id)
                    elif status == 1:
                        num_of_inprogress_meeting += 1
                    elif status == 0:
                        num_of_notStarted_meeting += 1

        num_of_current_member_in_ilt = db.query(MdlIltMembers.member_id).filter(MdlIltMembers.ilt_id == ilt_id, 
                                                                                MdlIltMembers.is_active==True).count()

        for mid in list_of_ended_meeting_ids:

            member_meeting_response_id_list = [map_record.meeting_response_id
                                               for map_record in db.query(MdlIltMeetingResponses)
                                               .filter(MdlIltMeetingResponses.meeting_id == mid,
                                                       MdlIltMeetingResponses.is_active==True)
                                               .all()
                                               ]

            member_meeting_responce_records = (db.query(MdlMeetingsResponse)
                                               .filter(MdlMeetingsResponse.id.in_(member_meeting_response_id_list))
                                                .all())
            num_of_member_in_ilt = len(member_meeting_response_id_list)
        #  meeting end time
            meetingEndTime,meetingSchedulaDate = (db.query(MdlMeetings.end_at,MdlMeetings.schedule_start_at)
                                .filter(MdlMeetings.id == mid).one_or_none())
        # attandence
            attandence_nominator = sum([record.attendance_flag
                                        for record in member_meeting_responce_records])

            attandence_denominator = num_of_member_in_ilt
            avg_attendence = {
                        "percentage": attandence_nominator*100/attandence_denominator,
                        "total": attandence_denominator
                    }

        # rating:
            mid_ratings = [record.rating for record in member_meeting_responce_records if record.rating]
            avg_rating = 0
            if mid_ratings:
                rating_nominator = sum(mid_ratings)
                rating_denominator = len(mid_ratings)
                avg_rating = {
                        "percentage": (rating_nominator/rating_denominator),
                        "total": rating_denominator
                    }
            else:
                avg_rating = PercentageData()
        # rock_on_track
            avg_rock = get_rock_aggegrates_for_meeting(ilt_id = ilt_id, meeting_id = mid, db=db)
            

        # issue
            list_of_list_of_issue_records = [db.query(MdlIltissue)
                                             .filter(MdlIltissue.meeting_response_id == m_r_id, 
                                                     MdlIltissue.is_active==True)
                                             .all()
                                             for m_r_id in member_meeting_response_id_list]
            num_of_issue_raised =  sum(db.query(MdlIltissue.issue_id)
                                             .filter(and_(MdlIltissue.meeting_response_id == m_r_id,
                                                          MdlIltissue.parent_meeting_responce_id == m_r_id,
                                                          MdlIltissue.is_active==True))
                                             .count()
                                             for m_r_id in member_meeting_response_id_list)
            num_of_issue_resolved = 0
            
            issue_id_list = []
            avg_issueResolve = []
            avg_issueObj={}
            if list_of_list_of_issue_records:
                for record in list_of_list_of_issue_records:
                    if record:
                        for r in record:
                            issue_id_list.append(r.issue_id)
                    else:
                        pass
            denominator = 0
            numOfIssueRepeat=0
            issue_nominators = {
                    'resolve': 0,
                    'recognizePerformance': 0,
                    'teacherSupport': 0,
                    'leaderSupport': 0,
                    'advanceEquity': 0,
                    'othersFlag': 0
            }
            if issue_id_list:
                # meetings_issue_resolve_list = [db.query(Mdl_issue)
                #                                .get(issue_id)
                #                                .resolves_flag
                #                                for issue_id in issue_id_list]
                for issue_id in issue_id_list:
                    numOfIssueRepeat += (db.query(MdlIltissue)
                                             .filter(MdlIltissue.issue_id == issue_id, MdlIltissue.is_active == True)
                                             .count())
                    issue_re = db.query(Mdl_issue).get(issue_id)
                    issue_nominators['resolve'] += int(issue_re.resolves_flag)
                    issue_nominators['recognizePerformance'] += int(issue_re.recognize_performance_flag)
                    issue_nominators['teacherSupport'] += int(issue_re.teacher_support_flag)
                    issue_nominators['leaderSupport'] += int(issue_re.leader_support_flag)
                    issue_nominators['advanceEquity'] += int(issue_re.advance_equality_flag)
                    issue_nominators['othersFlag'] += int(issue_re.others_flag)
                    denominator += 1
                    if issue_re.resolves_flag == True:
                        resolved_by_meeting_id = (db.query(MdlMeetings.id)
                                                    .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                                    .filter(MdlIltMeetings.ilt_id == ilt_id)
                                                    .filter(MdlMeetings.start_at<issue_re.issue_resolve_date)
                                                    .order_by(MdlMeetings.start_at.desc())
                                                    .first()
                                                    )
                        
                        num_of_issue_resolved += 1 if resolved_by_meeting_id == mid else 0


            avg_issueObj = {flag: {'percentage':(issue_nominators[flag]/denominator)*100 if denominator > 0 else 0, 'total':denominator} 
                                            for flag in issue_nominators 
                            }
            if numOfIssueRepeat>0:
                avg_issueObj["avgIssueRepeat"] =  {"percentage":round(numOfIssueRepeat/denominator, 1), "total":denominator}
            else:
                avg_issueObj["avgIssueRepeat"] =  {"percentage":0 if denominator==0 else 0, "total":denominator} 
            avg_issueObj["totalIssues"] = denominator
            avg_issueObj["numIssueRaised"]= num_of_issue_raised
            avg_issueObj["numIssueResolved"] = num_of_issue_resolved
            # To-Do
            list_list_of_toDo_records = (db.query(MdlIlt_ToDoTask)
                                         .filter(MdlIlt_ToDoTask.meeting_response_id == m_r_id,
                                                 MdlIlt_ToDoTask.is_active==True)
                                         .all()
                                         for m_r_id in member_meeting_response_id_list)
            meeting_todo_record_list = []
            avg_ToDo = {}
            ToDo_denominator = 0
            if list_list_of_toDo_records:
                for list_todo_record in list_list_of_toDo_records:
                    for todo_record in list_todo_record:
                        meeting_todo_record_list.append(todo_record.status)

            if meeting_todo_record_list:
                ToDo_nominator = sum(meeting_todo_record_list)
                ToDo_denominator = len(meeting_todo_record_list)
                avg_ToDo = {
                        "percentage": (ToDo_nominator/ToDo_denominator)*100,
                        "total": ToDo_denominator
                    }
            else:
                avg_ToDo = PercentageData()

            list_of_meeting_obj.append(
                {
                    "id": ilt_id,
                    "meetingId":mid,
                    "meetingSchedulaDate":meetingSchedulaDate,
                    "meetingEndDate":meetingEndTime,
                    "attendancePercentage": avg_attendence,
                    "rockOnTrack": avg_rock,
                    "avgRatings": avg_rating,
                    "avgtoDo": avg_ToDo,
                    "issues": avg_issueObj 
                })

        return {
            "id": ilt_id,
            "numOfEndMeeting": num_of_ended_meeting,
            "numOfNotStartedMeeting": num_of_notStarted_meeting,
            "numOfInprogressMeeting": num_of_inprogress_meeting,
            "numOfMembersInIlt": num_of_current_member_in_ilt,
            "meetings": list_of_meeting_obj
        }

    def get_ilt_Meeting_dashboard_info(self, user_id: int, meetingId:int, ilt_id: int, db: Session):
        # check user
        user_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if user_record is None:
            raise CustomException(404,  "User not found")
        meeting_reco = db.query(MdlIltMeetings).filter(
                MdlIltMeetings.ilt_id == ilt_id, MdlIltMeetings.ilt_meeting_id== meetingId).one_or_none()
        if meeting_reco is None:
            raise CustomException(404,  "meeting id is not associated with iltId ")
        if user_record.role_id > 4:
            raise CustomException(404,  "You don't have permission, Please contact administrative.")
        
        # num_of_ended_meeting = 0
        # num_of_notStarted_meeting = 0
        # num_of_inprogress_meeting = 0
        num_of_member_in_ilt = 0
        list_of_ended_meeting_ids = []
        list_of_meeting_obj = []
        
        meeting_records = (db.query(MdlMeetings)
                                .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                .filter(MdlIltMeetings.ilt_id == ilt_id, MdlIltMeetings.ilt_meeting_id== meetingId)
                                .order_by(MdlMeetings.schedule_start_at.asc())
                                .all()
                                )
 

        if not meeting_records:
            raise CustomException(404,  "No records found.")
        
        for meeting_record in meeting_records:
            status = calculate_meeting_status(
                schedule_start_at=meeting_record.schedule_start_at,
                start_at=meeting_record.start_at if meeting_record.start_at else 0,
                end_at=meeting_record.end_at if meeting_record.end_at else 0)
            if status == 2:
                list_of_ended_meeting_ids.append(meeting_record.id)
            else:
                raise CustomException(404,  "Please make sure your Meeting is not ended")

        members_list = [map_record.member_id
                        for map_record in db.query(MdlIltMembers)
                        .filter(MdlIltMembers.ilt_id == ilt_id, MdlIltMembers.is_active==True)
                        .all()]
        num_of_current_member_in_ilt = len(members_list)
        print("num_of_current_member_in_ilt", num_of_current_member_in_ilt)
        for mid in list_of_ended_meeting_ids:

            member_meeting_response_id_list = [map_record.meeting_response_id
                                               for map_record in db.query(MdlIltMeetingResponses)
                                               .filter(MdlIltMeetingResponses.meeting_id == mid,
                                                       MdlIltMeetingResponses.is_active==True)
                                               .all()
                                               ]

            member_meeting_responce_records = (db.query(MdlMeetingsResponse)
                                               .filter(MdlMeetingsResponse.id.in_(member_meeting_response_id_list))
                                                .all())
            num_of_member_in_ilt = len(member_meeting_response_id_list)
        #  meeting end time
            meetingEndTime = db.query(MdlMeetings).get(mid).end_at 
        # attandence
            attandence_nominator = sum([record.attendance_flag
                                        for record in member_meeting_responce_records])

            attandence_denominator = num_of_member_in_ilt
            avg_attendence = {
                        "percentage": attandence_nominator*100/attandence_denominator,
                        "total": attandence_denominator
                    }

        # rating :
            mid_ratings = [record.rating for record in member_meeting_responce_records if record.rating]
            avg_rating = 0
            if mid_ratings:
                rating_nominator = sum(mid_ratings)
                rating_denominator = len(mid_ratings)
                avg_rating = {
                        "percentage": (rating_nominator/rating_denominator),
                        "total": rating_denominator
                    }
            else:
                avg_rating = PercentageData()
        # rock_on_track
            avg_rock = get_rock_aggegrates_for_meeting(ilt_id = ilt_id, meeting_id = mid, db=db)

        # issue
            list_of_list_of_issue_records = [db.query(MdlIltissue)
                                             .filter(MdlIltissue.meeting_response_id == m_r_id, MdlIltissue.is_active == True)
                                             .all()
                                             for m_r_id in member_meeting_response_id_list]
            issue_id_list = []
            avg_issueResolve = []
            avg_issueObj={}
            if list_of_list_of_issue_records:
                for record in list_of_list_of_issue_records:
                    if record:
                        for r in record:
                            issue_id_list.append(r.issue_id)
                    else:
                        pass
            denominator = 0
            numOfIssueRepeat=0
            issue_nominators = {
                    'resolve': 0,
                    'recognizePerformance': 0,
                    'teacherSupport': 0,
                    'leaderSupport': 0,
                    'advanceEquity': 0,
                    'othersFlag': 0
            }
            if issue_id_list:
                meetings_issue_resolve_list = [db.query(Mdl_issue)
                                               .get(issue_id)
                                               .resolves_flag
                                               for issue_id in issue_id_list]
                for issue_id in issue_id_list:
                    numOfIssueRepeat += (db.query(MdlIltissue)
                                         .filter(MdlIltissue.issue_id == issue_id, MdlIltissue.is_active == True)
                                         .count())
                    issue_re = db.query(Mdl_issue).get(issue_id)
                    issue_nominators['resolve'] += int(issue_re.resolves_flag)
                    issue_nominators['recognizePerformance'] += int(issue_re.recognize_performance_flag)
                    issue_nominators['teacherSupport'] += int(issue_re.teacher_support_flag)
                    issue_nominators['leaderSupport'] += int(issue_re.leader_support_flag)
                    issue_nominators['advanceEquity'] += int(issue_re.advance_equality_flag)
                    issue_nominators['othersFlag'] += int(issue_re.others_flag)
                    denominator += 1
            avg_issueObj = {flag: {'percentage':(issue_nominators[flag]/denominator)*100 if denominator > 0 else 0, 'total':denominator} 
                                            for flag in issue_nominators 
                            }
            if numOfIssueRepeat>0:
                avg_issueObj["avgIssueRepeat"] =  {"percentage":round(numOfIssueRepeat/denominator, 1), "total":denominator}
            else:
                avg_issueObj["avgIssueRepeat"] =  {"percentage":0 if denominator==0 else 0, "total":denominator} 
            avg_issueObj["totalIssues"] = denominator

            # To-Do
            list_list_of_toDo_records = (db.query(MdlIlt_ToDoTask)
                                         .filter(MdlIlt_ToDoTask.meeting_response_id == m_r_id,
                                                 MdlIlt_ToDoTask.is_active==True)
                                         .all()
                                         for m_r_id in member_meeting_response_id_list)
            meeting_todo_record_list = []
            avg_ToDo = {}
            ToDo_denominator = 0
            if list_list_of_toDo_records:
                for list_todo_record in list_list_of_toDo_records:
                    for todo_record in list_todo_record:
                        meeting_todo_record_list.append(todo_record.status)

            if meeting_todo_record_list:
                ToDo_nominator = sum(meeting_todo_record_list)
                ToDo_denominator = len(meeting_todo_record_list)
                avg_ToDo = {
                        "percentage": (ToDo_nominator/ToDo_denominator)*100,
                        "total": ToDo_denominator
                    }
            else:
                avg_ToDo = PercentageData()

            list_of_meeting_obj.append(
                {
                    "id": ilt_id,
                    "meetingId":mid,
                    "meetingEndDate":meetingEndTime,
                    "attendancePercentage": avg_attendence,
                    "rockOnTrack": avg_rock,
                    "avgRatings": avg_rating,
                    "avgtoDo": avg_ToDo,
                    "issues": avg_issueObj 
                })

        return {
            "id": ilt_id, 
            "numOfMembersInIlt": num_of_current_member_in_ilt,
            "meetings": list_of_meeting_obj[0]
        }
    
    def get_detailed_dashboard_info(self, user_id: int, db: Session, FilterParamaters:DashboardFilterParamaters=DashboardFilterParamaters() ): # school_id:list, distict_id:list,
        # check user
        user_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if user_record is None:
            raise CustomException(404,  "User not found")
        # if user_record.role_id<3:
        #     raise CustomException(404,  "This User is not allowed to perform this action")
        total_num_of_ended_meeting = 0
        total_num_of_notStarted_meeting = 0
        total_num_of_inprogress_meeting = 0
        list_of_Summary = []
        list_of_schoolId = get_associated_schoolId_wrt_role(user_id= user_id, role_id = user_record.role_id, 
                                                            FilterParamaters=FilterParamaters, db=db)
        for s_id in list_of_schoolId:
            num_of_ended_meeting = 0
            num_of_notStarted_meeting = 0
            num_of_inprogress_meeting = 0
            num_of_member_in_ilt = 0
            start_date= FilterParamaters.startDate     
            end_date = FilterParamaters.endDate
            list_of_ended_meeting_ids = []
            list_of_ilt = []
            SummaryDataObj = SummaryData()
        
        #  1. fetch all ilt_id based on school id or ids  note : for district_aggregate_info s_id is list_of_school_ids
            list_of_ilt = [id for id, in  db.query(MdlIlts.id).filter(MdlIlts.school_id.in_(s_id)).all()]
        #   2. get all meeting's records within the school 
            subquery = (db.query(MdlMeetings)
                                    .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                    .filter(MdlIltMeetings.ilt_id.in_(list_of_ilt)))
                           
            if start_date and end_date:
                subquery = subquery.filter(and_(MdlMeetings.schedule_start_at>start_date,
                                           MdlMeetings.schedule_start_at<end_date))

            list_meeting_records = (subquery.order_by(MdlMeetings.schedule_start_at.asc()).all())
            # rock
            SummaryDataObj.rockOnTrack = get_rock_aggegrates(list_of_ilt = list_of_ilt, db=db)

            for meeting_record in list_meeting_records:
                status = calculate_meeting_status(
                    schedule_start_at=meeting_record.schedule_start_at,
                    start_at=meeting_record.start_at if meeting_record.start_at else 0,
                    end_at=meeting_record.end_at if meeting_record.end_at else 0)
                if status == 2:
                    num_of_ended_meeting += 1
                    list_of_ended_meeting_ids.append(meeting_record.id)
                elif status == 1:
                    num_of_inprogress_meeting += 1
                elif status == 0:
                    num_of_notStarted_meeting += 1

            
          # 3. cal and aggregate all ended meeting's summary
            for mid in list_of_ended_meeting_ids:

                member_meeting_response_id_list = [map_record.meeting_response_id
                                                for map_record in db.query(MdlIltMeetingResponses)
                                                .filter(MdlIltMeetingResponses.meeting_id == mid,
                                                        MdlIltMeetingResponses.is_active==True)
                                                .all()
                                                ]
                member_meeting_responce_records = (db.query(MdlMeetingsResponse)
                                                .filter(MdlMeetingsResponse.id.in_( member_meeting_response_id_list))
                                                .all())
                num_of_member_in_ilt = len(member_meeting_response_id_list) 

            # attandence
                attandence_nominator = sum([record.attendance_flag
                                            for record in member_meeting_responce_records])
                attandence_denominator = num_of_member_in_ilt

                SummaryDataObj.attendancePercentage.percentage += (attandence_nominator*100/attandence_denominator)
                SummaryDataObj.attendancePercentage.total += 1
            # rating :
                mid_ratings = [record.rating for record in member_meeting_responce_records if record.rating]
                avg_rating = 0
                if mid_ratings:
                    rating_nominator = sum(mid_ratings)
                    rating_denominator = len(mid_ratings)

                    SummaryDataObj.avgRatings.percentage += (rating_nominator/rating_denominator)
                SummaryDataObj.avgRatings.total += 1

            # issue
                list_of_list_of_issue_records = [db.query(MdlIltissue)
                                                .filter(MdlIltissue.meeting_response_id == m_r_id
                                                        , MdlIltissue.is_active==True)
                                                .all()
                                                for m_r_id in member_meeting_response_id_list]
                issue_id_list = []
                avg_issueResolve = []
                avg_issueObj={}
                if list_of_list_of_issue_records:
                    for record in list_of_list_of_issue_records:
                        if record:
                            for r in record:
                                issue_id_list.append(r.issue_id)
                        else:
                            pass
                denominator = 0
                numOfIssueRepeat=0
                issue_nominators = {
                                    'resolve': 0,
                                    'recognizePerformance': 0,
                                    'teacherSupport': 0,
                                    'leaderSupport': 0,
                                    'advanceEquity': 0,
                                    'othersFlag': 0,
                                    "avgIssueRepeat":0
                }
                if issue_id_list:
                    # meetings_issue_resolve_list = [db.query(Mdl_issue)
                    #                             .get(issue_id)
                    #                             .resolves_flag
                    #                             for issue_id in issue_id_list]
                    for issue_id in issue_id_list:
                        issue_nominators['avgIssueRepeat'] += (db.query(func.count(MdlIltissue.id))
                                                                .filter(MdlIltissue.issue_id==issue_id)
                                                                .scalar())
                        issue_re = db.query(Mdl_issue).get(issue_id)
                        issue_nominators['resolve'] += int(issue_re.resolves_flag)
                        issue_nominators['recognizePerformance'] += int(issue_re.recognize_performance_flag)
                        issue_nominators['teacherSupport'] += int(issue_re.teacher_support_flag)
                        issue_nominators['leaderSupport'] += int(issue_re.leader_support_flag)
                        issue_nominators['advanceEquity'] += int(issue_re.advance_equality_flag)
                        issue_nominators['othersFlag'] += int(issue_re.others_flag)
                        denominator += 1

                avg_issueObj["totalIssues"] = denominator
                for key, value in vars(SummaryDataObj.issues).items():

                    setattr(SummaryDataObj.issues, key, PercentageData(value.percentage +(issue_nominators[key]/denominator if denominator > 0 else 0)
                                                                       ,value.total+1)) 

                # To-Do
                list_list_of_toDo_records = (db.query(MdlIlt_ToDoTask)
                                            .filter(MdlIlt_ToDoTask.meeting_response_id == m_r_id,
                                                    MdlIlt_ToDoTask.is_active==True)
                                            .all()
                                            for m_r_id in member_meeting_response_id_list)
                meeting_todo_record_list = []
                avg_ToDo = {}
                ToDo_denominator = 0
                if list_list_of_toDo_records:
                    for list_todo_record in list_list_of_toDo_records:
                        for todo_record in list_todo_record:
                            meeting_todo_record_list.append(todo_record.status)

                if meeting_todo_record_list:
                    ToDo_nominator = sum(meeting_todo_record_list)
                    ToDo_denominator = len(meeting_todo_record_list)
                    avg_ToDo = {
                            "percentage": (ToDo_nominator/ToDo_denominator)*100,
                            "total": ToDo_denominator
                        }
                    SummaryDataObj.avgtoDo.percentage += (ToDo_nominator*100/ToDo_denominator)
                SummaryDataObj.avgtoDo.total += 1
                
          # 4. take avg and then append it to list_of_school_Summary
            if list_of_ended_meeting_ids:

                total_num_of_ended_meeting += len(list_of_ended_meeting_ids)
                total_num_of_notStarted_meeting += num_of_notStarted_meeting
                total_num_of_inprogress_meeting += num_of_inprogress_meeting
                
                SummaryDataObj.numOfEndMeeting = len(list_of_ended_meeting_ids)
                SummaryDataObj.numOfInprogressMeeting = num_of_inprogress_meeting
                SummaryDataObj.numOfNotStartedMeeting = num_of_notStarted_meeting
                
                SummaryDataObj.numOfMembers = db.query(MdlIltMembers).filter(MdlIltMembers.ilt_id.in_(list_of_ilt), 
                                                                             MdlIltMembers.is_active==True).count()
                if FilterParamaters.districtAggregateFlag ==True:
                   dis_id, = db.query(MdlSchools.district).filter(MdlSchools.id == s_id[0]).one()   
                   SummaryDataObj.id = dis_id
                   SummaryDataObj.name, = db.query(MdlDistrict.name).filter(MdlDistrict.id==dis_id).one()
                   
                else:
                    school_re = db.query(MdlSchools).filter(MdlSchools.id == s_id[0]).one()
                    SummaryDataObj.name = school_re.name
                    SummaryDataObj.id = school_re.id

                for key, value in vars(SummaryDataObj).items():
                        if key in ["attendancePercentage", "avgRatings", "avgtoDo", "issues"]:
                            if key == "issues":
                                for key1, value1 in vars(SummaryDataObj.issues).items():
                                    if key1 =="avgIssueRepeat":
                                        setattr(SummaryDataObj.issues, key1, PercentageData(round(value1.percentage/value1.total, 1) if value1.total > 0 else 0, value1.total))
                                        continue
                                    setattr(SummaryDataObj.issues, key1, PercentageData(round((value1.percentage/value1.total)*100, 2) if value1.total > 0 else 0, value1.total))   
                            else:
                                setattr(SummaryDataObj, key, PercentageData(round(value.percentage/value.total, 2) if value.total > 0 else 0, value.total))
                
                list_of_Summary.append(SummaryDataObj)
        final_val = {
            "totalNumOfEndMeeting": total_num_of_ended_meeting,
            "totalNumOfNotStartedMeeting": total_num_of_notStarted_meeting,
            "totalNumOfInprogressMeeting": total_num_of_inprogress_meeting,
        }

        if  FilterParamaters.districtAggregateFlag ==True:
            final_val["districts"] = list_of_Summary
        else:
            final_val["schools"] = list_of_Summary

        return final_val