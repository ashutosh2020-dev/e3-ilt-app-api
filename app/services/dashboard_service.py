from sqlalchemy.orm import Session
from app.models import MdlUsers, MdlIltMeetings, MdlMeetings, MdlMeeting_rocks,\
    MdlIltMembers, MdlIltMeetingResponses, MdlMeetingsResponse, MdlIltissue,\
    Mdl_issue, MdlIlt_ToDoTask, MdlIlts, MdlSchools
from app.schemas.dashboard_schemas import SummaryData, PercentageData, DashboardFilterParamaters
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
        if FilterParamaters:
            if FilterParamaters.distict_id or FilterParamaters.school_id:
                if role_id<4:
                    raise CustomException(404,  "This User is not allowed to perform this action")
                if FilterParamaters.distict_id:
                    list_of_school_id.extend([id for id, in db.query(MdlSchools.id).filter(MdlSchools.district.in_(FilterParamaters.distict_id)).distinct()])
                if FilterParamaters.school_id:
                    list_of_school_id.extend(FilterParamaters.school_id)

                return list_of_school_id

        # for ilt
        if role_id==3:
            # extend child facilitator
            user_id_list.extend([u_re.id
                                 for u_re in db.query(MdlUsers).filter(MdlUsers.parent_user_id == user_id).all()])
            # remove duplicates
            user_id_list = list(set(user_id_list))
            # get all ilt where user_id is member
            list_ilts.extend([record.ilt_id for record in db.query(
                                            MdlIltMembers).filter(MdlIltMembers.member_id == user_id).all()])
            for  uid in user_id_list:
                list_ilts.extend([record.id for record in db.query(
                    MdlIlts).filter(MdlIlts.owner_id == uid).all()])
            unique_school_ids = [id for id, in db.query(MdlIlts.school_id)
                                 .filter(MdlIlts.id.in_(list_ilts))
                                 .distinct()
                                 ]
            list_of_school_id.extend(unique_school_ids)

        elif role_id==4:
            unique_school_ids = [id for id, in db.query(MdlIlts.school_id).distinct()]
            list_of_school_id.extend(unique_school_ids)

        return list_of_school_id


class DashboardService:
    def get_ilt_Meetings_dashboard_info(self, user_id: int, ilt_id: int, db: Session):
        # check user
        user_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if user_record is None:
            raise CustomException(404,  "User not found")
        num_of_ended_meeting = 0
        num_of_notStarted_meeting = 0
        num_of_inprogress_meeting = 0
        num_of_member_in_ilt = 0

        list_of_ended_meeting_ids = []
        list_of_meeting_obj = []
        if user_record.role_id <= 4:

            list_meeting_records = (db.query(MdlMeetings)
                                    .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                    .filter(MdlIltMeetings.ilt_id == ilt_id)
                                    .order_by(MdlMeetings.schedule_start_at.asc())
                                    .all()
                                    )
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

        num_of_current_member_in_ilt = db.query(MdlIltMembers.member_id).filter(MdlIltMembers.ilt_id == ilt_id).count()

        for mid in list_of_ended_meeting_ids:

            member_meeting_response_id_list = [map_record.meeting_response_id
                                               for map_record in db.query(MdlIltMeetingResponses)
                                               .filter(MdlIltMeetingResponses.meeting_id == mid)
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
            mid_rocks = [
                record.onTrack for record in member_meeting_responce_records if record.rockName]
            avg_rock = 0
            if mid_rocks:
                rock_nominator = sum(mid_rocks)
                rock_denominator = len(mid_rocks)
                avg_rock = {
                        "percentage": (rock_nominator/rock_denominator)*100,
                        "total": rock_denominator
                    }
            else:
                avg_rock = PercentageData()

        # issue
            list_of_list_of_issue_records = [db.query(MdlIltissue)
                                             .filter(MdlIltissue.meeting_response_id == m_r_id)
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
                    'advanceEquality': 0,
                    'othersFlag': 0
            }
            if issue_id_list:
                meetings_issue_resolve_list = [db.query(Mdl_issue)
                                               .get(issue_id)
                                               .resolves_flag
                                               for issue_id in issue_id_list]
                for issue_id in issue_id_list:
                    numOfIssueRepeat += len([record.meeting_response_id for record in db.query(MdlIltissue).filter(MdlIltissue.issue_id==issue_id).all()])
                    issue_re = db.query(Mdl_issue).get(issue_id)
                    issue_nominators['resolve'] += int(issue_re.resolves_flag)
                    issue_nominators['recognizePerformance'] += int(issue_re.recognize_performance_flag)
                    issue_nominators['teacherSupport'] += int(issue_re.teacher_support_flag)
                    issue_nominators['leaderSupport'] += int(issue_re.leader_support_flag)
                    issue_nominators['advanceEquality'] += int(issue_re.advance_equality_flag)
                    issue_nominators['othersFlag'] += int(issue_re.others_flag)
                    denominator += 1
            avg_issueObj = {flag: {'percentage':(issue_nominators[flag]/denominator)*100 if denominator > 0 else 0, 'total':denominator} 
                                            for flag in issue_nominators 
                            }
            if numOfIssueRepeat>0:
                avg_issueObj["avgIssueRepeat"] =  {"percentage":round(numOfIssueRepeat/denominator, 0), "total":denominator}
            else:
                avg_issueObj["avgIssueRepeat"] =  {"percentage":0 if denominator==0 else 0, "total":denominator} 
            avg_issueObj["totalIssues"] = denominator

            # To-Do
            list_list_of_toDo_records = (db.query(MdlIlt_ToDoTask)
                                         .filter(MdlIlt_ToDoTask.meeting_response_id == m_r_id)
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
                        .filter(MdlIltMembers.ilt_id == ilt_id)
                        .all()]
        num_of_current_member_in_ilt = len(members_list)
        print("num_of_current_member_in_ilt", num_of_current_member_in_ilt)
        for mid in list_of_ended_meeting_ids:

            member_meeting_response_id_list = [map_record.meeting_response_id
                                               for map_record in db.query(MdlIltMeetingResponses)
                                               .filter(MdlIltMeetingResponses.meeting_id == mid)
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
            mid_rocks = [
                record.onTrack for record in member_meeting_responce_records if record.rockName]
            avg_rock = 0
            if mid_rocks:
                rock_nominator = sum(mid_rocks)
                rock_denominator = len(mid_rocks)
                avg_rock = {
                        "percentage": (rock_nominator/rock_denominator)*100,
                        "total": rock_denominator
                    }
            else:
                avg_rock = PercentageData()

        # issue
            list_of_list_of_issue_records = [db.query(MdlIltissue)
                                             .filter(MdlIltissue.meeting_response_id == m_r_id)
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
                    'advanceEquality': 0,
                    'othersFlag': 0
            }
            if issue_id_list:
                meetings_issue_resolve_list = [db.query(Mdl_issue)
                                               .get(issue_id)
                                               .resolves_flag
                                               for issue_id in issue_id_list]
                for issue_id in issue_id_list:
                    numOfIssueRepeat += len([record.meeting_response_id for record in db.query(MdlIltissue).filter(MdlIltissue.issue_id==issue_id).all()])
                    issue_re = db.query(Mdl_issue).get(issue_id)
                    issue_nominators['resolve'] += int(issue_re.resolves_flag)
                    issue_nominators['recognizePerformance'] += int(issue_re.recognize_performance_flag)
                    issue_nominators['teacherSupport'] += int(issue_re.teacher_support_flag)
                    issue_nominators['leaderSupport'] += int(issue_re.leader_support_flag)
                    issue_nominators['advanceEquality'] += int(issue_re.advance_equality_flag)
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
                                         .filter(MdlIlt_ToDoTask.meeting_response_id == m_r_id)
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
            "meetings": list_of_meeting_obj
        }
    
    def get_detailed_dashboard_info(self, user_id: int, db: Session, FilterParamaters:DashboardFilterParamaters=""): # school_id:list, distict_id:list,
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
        list_of_school_Summary = []
        list_of_schoolId = get_associated_schoolId_wrt_role(user_id= user_id,role_id = user_record.role_id, 
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

         #  1. fetch all ilt_id based on school id
            list_of_ilt = [re.id for re in  db.query(MdlIlts).filter(MdlIlts.school_id==s_id).all()]
        #   2. get all meeting's records within the school 
            subquery = (db.query(MdlMeetings)
                                    .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                    .filter(MdlIltMeetings.ilt_id.in_(list_of_ilt)))
                           
            if start_date and end_date:
                subquery = subquery.filter(MdlMeetings.schedule_start_at>start_date and
                                           MdlMeetings.schedule_start_at<end_date)

            list_meeting_records = (subquery.order_by(MdlMeetings.schedule_start_at.asc()).all())
            

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
                                                .filter(MdlIltMeetingResponses.meeting_id == mid)
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
                
            # rock_on_track
                mid_rocks = [
                    record.onTrack for record in member_meeting_responce_records if record.rockName]
                avg_rock = 0
                if mid_rocks:
                    rock_nominator = sum(mid_rocks)
                    rock_denominator = len(mid_rocks)
                    
                    SummaryDataObj.rockOnTrack.percentage += (rock_nominator*100/rock_denominator)
                SummaryDataObj.rockOnTrack.total += 1

            # issue
                list_of_list_of_issue_records = [db.query(MdlIltissue)
                                                .filter(MdlIltissue.meeting_response_id == m_r_id)
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
                                    'advanceEquality': 0,
                                    'othersFlag': 0,
                                    "avgIssueRepeat":0
                }
                if issue_id_list:
                    meetings_issue_resolve_list = [db.query(Mdl_issue)
                                                .get(issue_id)
                                                .resolves_flag
                                                for issue_id in issue_id_list]
                    for issue_id in issue_id_list:
                        issue_nominators['avgIssueRepeat'] += db.query(MdlIltissue).filter(MdlIltissue.issue_id == issue_id).count()
                        issue_re = db.query(Mdl_issue).get(issue_id)
                        issue_nominators['resolve'] += int(issue_re.resolves_flag)
                        issue_nominators['recognizePerformance'] += int(issue_re.recognize_performance_flag)
                        issue_nominators['teacherSupport'] += int(issue_re.teacher_support_flag)
                        issue_nominators['leaderSupport'] += int(issue_re.leader_support_flag)
                        issue_nominators['advanceEquality'] += int(issue_re.advance_equality_flag)
                        issue_nominators['othersFlag'] += int(issue_re.others_flag)
                        denominator += 1

                avg_issueObj["totalIssues"] = denominator
                for key, value in vars(SummaryDataObj.issues).items():

                    setattr(SummaryDataObj.issues, key, PercentageData(value.percentage +(issue_nominators[key]/denominator if denominator > 0 else 0)
                                                                       ,value.total+1)) 

                # To-Do
                list_list_of_toDo_records = (db.query(MdlIlt_ToDoTask)
                                            .filter(MdlIlt_ToDoTask.meeting_response_id == m_r_id)
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
                SummaryDataObj.numOfMembers = db.query(MdlIltMembers).filter(MdlIltMembers.ilt_id.in_(list_of_ilt)).count()
                school_re = db.query(MdlSchools).filter(MdlSchools.id == s_id).one()
                SummaryDataObj.schoolName = school_re.name
                SummaryDataObj.schoolId = school_re.id

                for key, value in vars(SummaryDataObj).items():
                        if key in ["attendancePercentage", "rockOnTrack", "avgRatings", "avgtoDo", "issues"]:
                            if key == "issues":
                                for key1, value1 in vars(SummaryDataObj.issues).items():
                                    if key1 =="avgIssueRepeat":
                                        setattr(SummaryDataObj.issues, key1, PercentageData(round(value1.percentage/value1.total, 1) if value1.total > 0 else 0, value1.total))
                                    setattr(SummaryDataObj.issues, key1, PercentageData(round((value1.percentage/value1.total)*100, 2) if value1.total > 0 else 0, value1.total))   
                            else:
                                setattr(SummaryDataObj, key, PercentageData(round(value.percentage/value.total, 2) if value.total > 0 else 0, value.total))

                list_of_school_Summary.append(SummaryDataObj)
        
        return {
            "totalNumOfEndMeeting": total_num_of_ended_meeting,
            "totalNumOfNotStartedMeeting": total_num_of_notStarted_meeting,
            "totalNumOfInprogressMeeting": total_num_of_inprogress_meeting,
            "schools": list_of_school_Summary
        }

