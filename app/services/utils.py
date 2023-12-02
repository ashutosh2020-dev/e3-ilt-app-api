
from app.models import MdlMeetings, MdlIltMeetings
from sqlalchemy import and_



def get_upcomming_meeting(ilt_id, db):
    upcoming_meeting_list = [i for i, in db.query(MdlMeetings.id,)
                            .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                            .filter(MdlIltMeetings.ilt_id == ilt_id)
                            .filter(MdlMeetings.end_at == None)
                            .all()
                            ]

    return upcoming_meeting_list
    