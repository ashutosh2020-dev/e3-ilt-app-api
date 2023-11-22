from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, UniqueConstraint, Text
import datetime
from app.config.database import Base


class MdlRoles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=False)


class MdlUsers(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fname = Column(String(255), nullable=False)
    lname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    number = Column(Integer, nullable=True)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"),
                     nullable=False, index=True)
    parent_user_id = Column(Integer, nullable=True)

    def verify_password(self, password):
        return self.password == password
    
class MdlDistrict(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)

class MdlSchools(Base):
    __tablename__ = "schools"
    __table_args__ = (UniqueConstraint('name', 'district'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    district = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)

class MdlDistrictMember(Base):
    __tablename__ = "districts_member_mapping"
    id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True )


class MdlIlts(Base):
    __tablename__ = "Ilts"
    __table_args__ = (UniqueConstraint('title', 'school_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False,
                        default=datetime.datetime.utcnow)
    created_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime, nullable=True)
    update_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True )
    owner_id =  Column(Integer, ForeignKey("users.id"), nullable=False, index=True )
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)


class MdlIltMembers(Base):
    __tablename__ = "Ilt_members_maping"
    __table_args__ = (UniqueConstraint('ilt_id', 'member_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    ilt_id = Column(Integer, ForeignKey("Ilts.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey(
        "users.id"), nullable=False, index=True)


class MdlMeetings(Base):
    __tablename__ = "Ilt_meetings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=True, default=None)
    schedule_start_at = Column(DateTime, nullable=False, default=None)
    start_at = Column(DateTime, nullable=True, default=None)
    end_at = Column(DateTime, nullable=True, default=None)
    note_taker_id = Column(Integer, ForeignKey("users.id", name="fk_note_taker_id"), nullable=True, index=True, default=None)

class MdlIltMeetings(Base):
    __tablename__ = "Ilt_meeting_maping"
    __table_args__ = (UniqueConstraint('ilt_id', 'ilt_meeting_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    ilt_id = Column(Integer, ForeignKey("Ilts.id"), nullable=False, index=True)
    ilt_meeting_id = Column(Integer, ForeignKey("Ilt_meetings.id"), nullable=False, index=True)


class MdlIltWhiteBoard(Base):
    __tablename__ = "Ilt_whiteboard"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=True)
    iltId = Column(Integer, ForeignKey("Ilts.id"), unique=True, nullable=False, index=True)

class MdlIltMeetingWhiteBoard(Base):
    __tablename__ = "Ilt_meeting_whiteboard"
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=True)
    meetingId =  Column(Integer, ForeignKey("Ilt_meetings.id"), unique=True, nullable=False, index=True)
    

class MdlMeetingsResponse(Base):
    __tablename__ = "meeting_response"
    id = Column(Integer, primary_key=True, autoincrement=True)
    attendance_flag = Column(Boolean, nullable=True, default=False)
    checkin_personal_best = Column(String(255), nullable=True, default=None)
    checkin_professional_best = Column(String(255), nullable=True, default=None)
    rating = Column(Integer,  nullable=True, default=None)
    feedback = Column(String(255), nullable=True, default="")
    notes = Column(String(255), nullable=True, default="")
    rockName = Column(String(255), nullable=True, default="")
    onTrack = Column(Boolean, nullable=True, default="")


class MdlIltMeetingResponses(Base):
    __tablename__ = "ilt_meeting_response_mapping"
    __table_args__ = (UniqueConstraint(
        'meeting_user_id', 'meeting_response_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey(
        "Ilt_meetings.id"), nullable=False, index=True)
    meeting_user_id = Column(Integer, ForeignKey(
        "users.id"), nullable=False, index=True)
    meeting_response_id = Column(Integer, ForeignKey(
        "meeting_response.id"), nullable=False, index=True)


class MdlRocks(Base):
    __tablename__ = "Ilt_rocks"
    __table_args__ = (UniqueConstraint('ilt_id', 'name'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    ilt_id = Column(Integer, ForeignKey("Ilts.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    on_track_flag = Column(Boolean, nullable=False)


class MdlRocks_members(Base):
    __tablename__ = "Rocks_member_mapping"
    __table_args__ = (UniqueConstraint('user_id', 'ilt_rock_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False, index=True)
    ilt_rock_id = Column(Integer, ForeignKey("Ilt_rocks.id"), nullable=False, index=True)
    is_rock_owner = Column(Boolean, nullable=False, default=False)
    is_rock_member = Column(Boolean, nullable=False, default=False)


class MdlIlt_ToDoTask(Base):
    __tablename__ = "Ilt_to_do_task"
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_response_id = Column(Integer, ForeignKey(
        "meeting_response.id"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(Boolean, nullable=False, default=False)
    parent_to_do_id = Column(Integer, nullable=True, default=None)


class Mdl_updates(Base):
    __tablename__ = "meeting_updates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_response_id = Column(Integer, ForeignKey(
        "meeting_response.id"), nullable=False, index=True)
    description = Column(String(255), nullable=False)


class MdlPriorities(Base):
    __tablename__ = "Ilt_priorities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)


class Mdl_issue(Base):
    __tablename__ = "issue"
    id = Column(Integer, primary_key=True, autoincrement=True)
    issue = Column(String(255), nullable=True)
    priority = Column(Integer, ForeignKey(
        "Ilt_priorities.id"), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False) 
    due_date = Column(DateTime, nullable=True)
    issue_resolve_date = Column(DateTime, nullable=True)
    resolves_flag = Column(Boolean, nullable=True)
    recognize_performance_flag = Column(Boolean, nullable=True)
    teacher_support_flag = Column(Boolean, nullable=True)
    leader_support_flag = Column(Boolean, nullable=True)
    advance_equality_flag = Column(Boolean, nullable=True)
    others_flag = Column(Boolean, nullable=True)


class MdlIltissue(Base):
    __tablename__ = "meeting_issue_mapping"
    __table_args__ = (UniqueConstraint('meeting_response_id', 'issue_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_response_id = Column(Integer, ForeignKey(
        "meeting_response.id"), nullable=False, index=True)
    issue_id = Column(Integer, ForeignKey("issue.id"),
                      nullable=False, index=True)
    parent_meeting_responce_id = Column(Integer, ForeignKey(
            "meeting_response.id"), nullable=False, index=True)


class MdlIltPriorities(Base):
    __tablename__ = "Ilt_issue_priorities_mapping"
    __table_args__ = (UniqueConstraint('issue_id', 'priorities_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey("issue.id"),
                      nullable=False, index=True)
    priorities_id = Column(Integer, ForeignKey(
        "Ilt_priorities.id"), nullable=False, index=True)
