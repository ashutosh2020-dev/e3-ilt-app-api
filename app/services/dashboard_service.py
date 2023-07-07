from sqlalchemy.orm import Session
from app.models import MdlUsers, MdlIltMeetings, MdlMeetings, MdlMeeting_rocks,\
                    MdlIltMembers, MdlIltMeetingResponses, MdlMeetingsResponse, MdlIltissue, Mdl_issue
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

class DashboardService:
    def get_ilt_dashboard_info(self, user_id:int, ilt_id :int, db: Session):
        # check user 
        user_record = db.query(MdlUsers).filter(MdlUsers.id==user_id).one_or_none()
        if user_record is None:
            raise CustomException(404,  "User not found")
        if user_record.role_id==3:
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
            current_time = datetime.now(timezone.utc)
            all_meeting_id_list = [m_record.ilt_meeting_id for m_record in db.query(MdlIltMeetings).filter(MdlIltMeetings.ilt_id==ilt_id).all()]
            members_list = [map_record.member_id for map_record in db.query(MdlIltMembers).filter(MdlIltMembers.ilt_id==ilt_id).all()]
            num_of_member_in_ilt = len(members_list) 
            avg_attendance_list =[]
            avg_rating_list =[]
            avg_rock_list =[]
            avg_issueResolve_list =[]
            
            for mid in all_meeting_id_list:
                select_mid = (db.query(MdlMeetings)
                                .filter(MdlMeetings.id==mid, 
                                        MdlMeetings.end_at<current_time)
                                .one_or_none())
                
                if select_mid:
                    member_meeting_response_id_list = [map_record.meeting_response_id 
                                                    for map_record in db.query(MdlIltMeetingResponses)
                                                    .filter(MdlIltMeetingResponses.meeting_id==mid)
                                                    .all()
                                                    ]
                    
                    member_meeting_responce_records = [db.query(MdlMeetingsResponse)
                                                        .filter(MdlMeetingsResponse.id==m_r_id).one() 
                                                        for m_r_id in member_meeting_response_id_list]
                ## attandence : calculate nominator by summing all user's attandence and denominator is len of all members
                    attandence_nominator = sum([record.attendance_flag
                                                    for record in member_meeting_responce_records])

                    attandence_denominator = num_of_member_in_ilt
                    avg_attendence = attandence_nominator/attandence_denominator
                    
                    avg_attendance_list.append(avg_attendence)
                    
                ## rating : 
                    rating_nominator = sum([record.rating
                                                    for record in member_meeting_responce_records])
                    rating_denominator = num_of_member_in_ilt * 5
                    avg_rating = rating_nominator/rating_denominator
                    avg_rating_list.append(avg_rating)
                ## rock_on_track
                        # total num of rock wrt member wrt meeting wrt ilt, then cal deno; for nominator cal   
                    rocks_list = [db.query(MdlMeeting_rocks)
                                                        .filter(MdlMeeting_rocks.ilt_meeting_response_id==m_r_id)
                                                        .one()
                                                        .on_track_flag 
                                                        for m_r_id in member_meeting_response_id_list]
                    rock_nominator = sum(rocks_list)
                    rock_denominator = len(rocks_list)
                    avg_rock = rock_nominator/ rock_denominator
                    avg_rock_list.append(avg_rock)
                ## issue
                    issue_id_record = [db.query(MdlIltissue)
                                            .filter(MdlIltissue.meeting_response_id==m_r_id)
                                            .all()
                                            for m_r_id in member_meeting_response_id_list]
                    issue_id_list = []
                    for record in issue_id_record:
                        for r in record:
                            issue_id_list.append(r.issue_id)

                    meetings_issue_resolve_list = [db.query(Mdl_issue)
                                            .filter(Mdl_issue.id==issue_id)
                                            .one()
                                            .resolves_flag
                                            for issue_id in issue_id_list]
                    issue_nominator = sum(meetings_issue_resolve_list)
                    issue_denominator = len(meetings_issue_resolve_list)
                    avg_issueResolve_list.append(issue_nominator/issue_denominator)

            aggregate_attandence = sum(avg_attendance_list)/len(avg_attendance_list) if avg_attendance_list  else 0
            aggregate_rock = sum(avg_rock_list)/len(avg_rock_list) if avg_rock_list else 0
            avg_rating = sum(avg_rating_list)/len(avg_rating_list) if avg_rating_list else 0 
            avg_issueResolve = sum(avg_issueResolve_list)/len(avg_issueResolve_list) if avg_issueResolve_list else 0
            avg_distribution_issue = sum(avg_issueResolve_list)/len(avg_issueResolve_list) if avg_issueResolve_list else 0

            return {
                "ilt_aggregate_attandence":aggregate_attandence,
                "aggregate_rock": aggregate_rock,
                "avg_rating": avg_rating,
                "avg_issueResolve": avg_issueResolve,
                "avg_distribution_issue": avg_distribution_issue
            }   
        except Exception as e:
             raise CustomException(500, f"unable to process your request, error - {e}")