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
    advanceEquityFlag : bool
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
    todoListId:Optional[int]=0
    description: str
    dueDate:datetime
    status: bool

class TodoList(BaseModel):
    todoItem: List[TodoData]

class meetingReasponceRock(BaseModel):
    rockName: str
    onTrack: Optional[bool]=None

class updates_schema(BaseModel):
    updateId:int
    description:str

class updatesData(BaseModel):
    descriptions:List[updates_schema]

class checkIn(BaseModel):
    personalBest:Optional[str]=None
    professionalBest:Optional[str]=None
    attendance:Optional[bool]=None

class feedback(BaseModel):
    rating:int
    feedback:str
    notes:str

class singleIssue(BaseModel):
    issueId:Optional[int]=0
    assignToResponceId: Optional[int] = 0
    meetingID: Optional[int] = 0
    issue: str
    priorityId: Optional[int] = 0
    date: datetime= Field(default_factory=lambda: datetime.now())
    resolvedFlag: bool
    recognizePerformanceFlag: bool
    teacherSupportFlag: bool
    leaderSupportFlag: bool
    advanceEquityFlag: bool
    othersFlag: bool

class IssueList(BaseModel):
    issues: List[singleIssue]


class RockInput(BaseModel):
    rockId: Optional[int]=None
    iltId:int
    name:str
    description:Optional[str]=""
    onTrack:Optional[bool] = False
    rockOwnerId:int
    rockMembers:Optional[List[int]] = []
    isComplete: Optional[bool] = None


class RockOutput():
    rockId: int
    iltId: int
    name: str
    description: str
    onTrack: bool
    rockOwner: List[Member]
    rockMembers: Optional[List[Member]] = []
    isComplete: bool
