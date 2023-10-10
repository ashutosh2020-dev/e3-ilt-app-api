from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MeetingData(BaseModel):
    scheduledStartDate: datetime
    meetingStart: Optional[datetime]=None
    meetingEnd: Optional[datetime]=None
    location: Optional[str]=None
    note_taker_id: Optional[int]=None

class rockData(BaseModel):
    iltId:int
    name:str
    description:str
    

class rockData_map(BaseModel):
    userId :List[int]
    iltId :int
    rockId :int
    rockOwnerId:int

class Status(BaseModel):
    status:Optional[int]=3

class PendingData(BaseModel):
    listOfIssueIds :List[int] 
    listOfToDoIds :List[int]
    futureMeetingId :int

class whiteboardData(BaseModel):
    description:Optional[str]=None

class whiteboardDataInfo():
    def __init__(self, iltId=0,meetingId=0):
        self.iltId=iltId
        self.meetingId=meetingId
        self.description=""