from sqlalchemy.orm import Session
from app.models import MdlUsers, MdlIltMeetings, MdlMeetings, MdlMeeting_rocks,\
    MdlIltMembers, MdlIltMeetingResponses, MdlMeetingsResponse, MdlIltissue, Mdl_issue, MdlIlt_ToDoTask
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
        # avg_attendance_list =[]
        # avg_rating_list =[]
        # avg_rock_list =[]
        # avg_issueResolve_list =[]
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

        members_list = [map_record.member_id
                        for map_record in db.query(MdlIltMembers)
                        .filter(MdlIltMembers.ilt_id == ilt_id)
                        .all()]
        num_of_member_in_ilt = len(members_list)

        for mid in list_of_ended_meeting_ids:

            member_meeting_response_id_list = [map_record.meeting_response_id
                                               for map_record in db.query(MdlIltMeetingResponses)
                                               .filter(MdlIltMeetingResponses.meeting_id == mid)
                                               .all()
                                               ]

            member_meeting_responce_records = [db.query(MdlMeetingsResponse)
                                               .filter(MdlMeetingsResponse.id == m_r_id).one()
                                               for m_r_id in member_meeting_response_id_list]
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
            mid_ratings = [
                record.rating for record in member_meeting_responce_records if record.rating]
            avg_rating = 0
            if mid_ratings:
                rating_nominator = sum(mid_ratings)
                rating_denominator = len(mid_ratings)*5
                avg_rating = {
                        "percentage": (rating_nominator/rating_denominator)*100,
                        "total": rating_denominator
                    }

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
                avg_issueObj["avgIssueRepeat"] =  {"percentage":(numOfIssueRepeat/denominator)*100, "total":denominator}
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
                        "percentage": ToDo_nominator/ToDo_denominator,
                        "total": ToDo_denominator
                    }

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
            "numOfMembersInIlt": num_of_member_in_ilt,
            "meetingsObj": list_of_meeting_obj
        }

    def get_dashboard_info(self, user_id: int, ilt_id: int, db: Session):
        # check user
        user_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if user_record is None:
            raise CustomException(404,  "User not found")
        if user_record.role_id == 3:
            """
                avg_last_ilts_meeting_in_district
                avg_num_ilt_meeting_in_district
                avg_attendance_in_district
                avg_rock_on_track_in_district
                avg_rating
                avg_issue
                distribution_of_issue
            """
            raise CustomException(404,  "Functionality is under-construction")

        try:
            current_time = datetime.now()
            all_meeting_id_list = [m_record.ilt_meeting_id
                                   for m_record in db.query(MdlIltMeetings)
                                   .filter(MdlIltMeetings.ilt_id == ilt_id)
                                   .all()]
            members_list = [map_record.member_id
                            for map_record in db.query(MdlIltMembers)
                            .filter(MdlIltMembers.ilt_id == ilt_id)
                            .all()]
            num_of_member_in_ilt = len(members_list)
            avg_attendance_list = []
            avg_rating_list = []
            avg_rock_list = []
            avg_issueResolve_list = []

            for mid in all_meeting_id_list:
                select_mid = (db.query(MdlMeetings)
                                .filter(MdlMeetings.id == mid,
                                        MdlMeetings.end_at < current_time)
                                .one_or_none())

                if select_mid:
                    member_meeting_response_id_list = [map_record.meeting_response_id
                                                       for map_record in db.query(MdlIltMeetingResponses)
                                                       .filter(MdlIltMeetingResponses.meeting_id == mid)
                                                       .all()
                                                       ]

                    member_meeting_responce_records = [db.query(MdlMeetingsResponse)
                                                       .filter(MdlMeetingsResponse.id == m_r_id).one()
                                                       for m_r_id in member_meeting_response_id_list]
                # attandence : calculate nominator by summing all user's attandence and denominator is len of all members
                    attandence_nominator = sum([record.attendance_flag
                                                for record in member_meeting_responce_records])

                    attandence_denominator = num_of_member_in_ilt
                    avg_attendence = attandence_nominator/attandence_denominator

                    avg_attendance_list.append(avg_attendence)

                # rating :
                    rating_nominator = sum([record.rating
                                            for record in member_meeting_responce_records])
                    rating_denominator = num_of_member_in_ilt * 5
                    avg_rating = rating_nominator/rating_denominator
                    avg_rating_list.append(avg_rating)
                # rock_on_track
                    # total num of rock wrt member wrt meeting wrt ilt, then cal deno; for nominator cal
                    rocks_list = [db.query(MdlMeeting_rocks)
                                  .filter(MdlMeeting_rocks.ilt_meeting_response_id == m_r_id)
                                  .one()
                                  .on_track_flag
                                  for m_r_id in member_meeting_response_id_list]
                    rock_nominator = sum(rocks_list)
                    rock_denominator = len(rocks_list)
                    avg_rock = rock_nominator / rock_denominator
                    avg_rock_list.append(avg_rock)
                # issue
                    issue_id_record = [db.query(MdlIltissue)
                                       .filter(MdlIltissue.meeting_response_id == m_r_id)
                                       .all()
                                       for m_r_id in member_meeting_response_id_list]
                    issue_id_list = []
                    for record in issue_id_record:
                        for r in record:
                            issue_id_list.append(r.issue_id)

                    meetings_issue_resolve_list = [db.query(Mdl_issue)
                                                   .filter(Mdl_issue.id == issue_id)
                                                   .one()
                                                   .resolves_flag
                                                   for issue_id in issue_id_list]
                    issue_nominator = sum(meetings_issue_resolve_list)
                    issue_denominator = len(meetings_issue_resolve_list)
                    avg_issueResolve_list.append(
                        issue_nominator/issue_denominator)

            aggregate_attandence = sum(
                avg_attendance_list)/len(avg_attendance_list) if avg_attendance_list else 0
            aggregate_rock = sum(avg_rock_list) / \
                len(avg_rock_list) if avg_rock_list else 0
            avg_rating = sum(avg_rating_list) / \
                len(avg_rating_list) if avg_rating_list else 0
            avg_issueResolve = sum(
                avg_issueResolve_list)/len(avg_issueResolve_list) if avg_issueResolve_list else 0
            avg_distribution_issue = sum(
                avg_issueResolve_list)/len(avg_issueResolve_list) if avg_issueResolve_list else 0

            return {
                "ilt_aggregate_attandence": aggregate_attandence,
                "aggregate_rock": aggregate_rock,
                "avg_rating": avg_rating,
                "avg_issueResolve": avg_issueResolve,
                "avg_distribution_issue": avg_distribution_issue
            }
        except Exception as e:
            raise CustomException(
                500, f"unable to process your request, error - {e}")
