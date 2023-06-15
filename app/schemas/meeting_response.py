from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
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
    attendance: bool =False
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