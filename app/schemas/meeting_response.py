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

class TodoItem(BaseModel):
    description: str
    dueDate: str="2023-05-23"
    status: str

class Issue(BaseModel):
    issueid: int
    issue: str
    priority: int
    created_at: str
    resolvedFlag: bool
    recognizePerformanceFlag: bool
    teacherSupportFlag: bool
    leaderSupportFlag: bool
    advanceEqualityFlag: bool
    othersFlag: bool

class MeetingResponse(BaseModel):
    iltMeetingResponseId: int
    iltMeetingId: int
    member: Member
    attendance: bool
    personalBest: str
    professionalBest: str
    rating: int
    feedback: str
    notes: str
    rocks: List[Rock]
    updates: List[str]
    todoList: List[TodoItem]
    issues: List[Issue]

class Duedate(BaseModel):
    Duedate:datetime

class Createdate(BaseModel):
    CreateAt:datetime