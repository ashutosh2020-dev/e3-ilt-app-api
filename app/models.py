from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, UniqueConstraint
import datetime
from app.config.database import Base

class MdlRoles(Base):
    __tablename__ = "roles"
    id =  Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

class MdlUsers(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fname  = Column(String, nullable=False)
    lname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    number = Column(Integer, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    parent_user_id = Column(Integer, nullable=False)

    def verify_password(self, password):
        return self.password == password

class MdlSchools(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    location = Column(String, nullable=False)
    district = Column(String, nullable=False)    

class MdlIlts(Base):
    __tablename__ = "Ilts"
    __table_args__ = (UniqueConstraint('title', 'school_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime,nullable=False, default=datetime.datetime.utcnow)
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    update_by = Column(String, nullable=True)
    owner_id = Column(Integer,  nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False, index=True)

class MdlIltMembers(Base):
    __tablename__ = "Ilt_members_maping"
    __table_args__ = (UniqueConstraint('ilt_id', 'member_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    ilt_id = Column(Integer, ForeignKey("Ilts.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

class MdlMeetings(Base):
    __tablename__ = "Ilt_meetings"
    id =  Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String, nullable=True, default=None)
    schedule_start_at = Column(DateTime, nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)

class MdlIltMeetings(Base):
    __tablename__ = "Ilt_meeting_maping"
    __table_args__ = (UniqueConstraint('ilt_id', 'ilt_meeting_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    ilt_id = Column(Integer, ForeignKey("Ilts.id"), nullable=False, index=True)
    ilt_meeting_id = Column(Integer, ForeignKey("Ilt_meetings.id"), nullable=False, index=True)

class MdlMeetingsResponse(Base):
    __tablename__ = "meeting_response"
    id = Column(Integer, primary_key=True, autoincrement=True)
    attendance_flag = Column(Boolean, nullable=True)
    checkin_personal_best = Column(String, nullable=True, default=None)
    checkin_professional_best = Column(String, nullable=True, default=None)
    rating = Column(Integer,  nullable=True, default=None)
    feedback = Column(String, nullable=True, default="")
    notes =  Column(String, nullable=True, default="")

class MdlIltMeetingResponses(Base):
    __tablename__ = "ilt_meeting_response_mapping"
    __table_args__ = (UniqueConstraint('meeting_user_id', 'meeting_response_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey("Ilt_meetings.id"), nullable=False, index=True)
    meeting_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    meeting_response_id = Column(Integer, ForeignKey("meeting_response.id"), nullable=False, index=True)
    
class MdlRocks(Base):
    __tablename__ = "Ilt_rocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ilt_id = Column(Integer, ForeignKey("Ilts.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    # on_track_flag = Column(Boolean, nullable=False)

class MdlIlt_rocks(Base):
    __tablename__ = "Ilt_user_rocks_mapping"
    __table_args__ = (UniqueConstraint('ilt_id','user_id', 'ilt_rock_id'),)
    id  =  Column(Integer, primary_key=True, autoincrement=True)
    ilt_id = Column(Integer, ForeignKey("Ilts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    ilt_rock_id = Column(Integer, ForeignKey("Ilt_rocks.id"), nullable=True, index=True)

class MdlMeeting_rocks(Base):
    __tablename__ = "Ilt_meeting_rocks_maping"
    __table_args__ = (UniqueConstraint('ilt_meeting_response_id', 'rock_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    ilt_meeting_response_id =  Column(Integer, ForeignKey("meeting_response.id"), nullable=False, index=True)
    rock_id = Column(Integer, ForeignKey("Ilt_rocks.id"), nullable=False, index=True)
    on_track_flag = Column(Boolean, nullable=False)

class MdlIlt_ToDoTask(Base):
    __tablename__ = "Ilt_to_do_task"
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_response_id = Column(Integer, ForeignKey("meeting_response.id"), nullable=False, index=True)
    description =  Column(String, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)

class Mdl_updates(Base):
    __tablename__ = "meeting_updates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_response_id = Column(Integer, ForeignKey("meeting_response.id"), nullable=False, index=True)
    description = Column(String, nullable=False)

class MdlPriorities(Base):
    __tablename__ = "Ilt_priorities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

class Mdl_issue(Base):
    __tablename__ = "issue"
    id = Column(Integer, primary_key=True, autoincrement=True)
    issue = Column(String, nullable=True)
    priority = Column(Integer, ForeignKey("Ilt_priorities.id"), nullable=True, index=True)
    created_at = Column(DateTime, nullable=True)
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
    meeting_response_id = Column(Integer, ForeignKey("meeting_response.id"), nullable=False, index=True)
    issue_id = Column(Integer, ForeignKey("issue.id"), nullable=False, index=True)

class MdlIltPriorities(Base):
    __tablename__ = "Ilt_issue_priorities_mapping"
    __table_args__ = (UniqueConstraint('issue_id', 'priorities_id'),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey("issue.id"), nullable=False, index=True)
    priorities_id = Column(Integer, ForeignKey("Ilt_priorities.id"), nullable=False, index=True)

