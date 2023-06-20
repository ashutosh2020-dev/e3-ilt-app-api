from typing import List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
class Member(BaseModel):
    userId: int
    firstName: str
    lastName: str

class Rock(BaseModel):
    rockId: int
    onTrack: bool
class Updates(BaseModel):
    id: int
    description: str

class TodoItem(BaseModel):
    id:int
    description: str
    dueDate: datetime
    status: str

class Issue(BaseModel):
    issueid: int
    issue: str
    priorityId: str
    # priorityId: int
    created_at: datetime
    resolvedFlag: bool
    recognizePerformanceFlag: bool
    teacherSupportFlag: bool
    leaderSupportFlag: bool
    advanceEqualityFlag: bool
    othersFlag: bool

class MeetingResponse(BaseModel):
    iltMeetingResponseId: int = 0
    iltMeetingId: int =0
    member: Member
    attendance: Optional[bool] = None
    personalBest: str = ""
    professionalBest: str = ""
    rating: int = 0
    feedback: str = ""
    notes: str = ""
    rocks: List[Rock]
    updates: List[Updates]
    todoList: List[TodoItem]
    issues: List[Issue]

class Duedate(BaseModel):
    Duedate:datetime

class Createdate(BaseModel):
    CreateAt:datetime

class TodoData(BaseModel):
    description: str
    duedate:datetime
    status: str

class TodoList(BaseModel):
    TodoItem: List[TodoData]

class RockUpdate(BaseModel):
    rock_id: int
    onTrack: bool

class updates_schema(BaseModel):
    description:str

class updatesData(BaseModel):
    descriptions:List[updates_schema]



class singleIssue(BaseModel):
    issue: str
    priorityId: Optional[int] = 0
    date: datetime= Field(default_factory=lambda: datetime.now(timezone.utc))
    resolvedFlag: bool
    recognizePerformanceFlag: bool
    teacherSupportFlag: bool
    leaderSupportFlag: bool
    advanceEqualityFlag: bool
    othersFlag: bool

class IssueList(BaseModel):
    issues: List[singleIssue]
