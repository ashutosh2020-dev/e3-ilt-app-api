from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MeetingData(BaseModel):
    scheduledStartDate: datetime
    meetingStart: datetime
    meetingEnd: datetime
    location: str

class rockData(BaseModel):
    iltId:int
    name:str
    description:str
    

class rockData_map(BaseModel):
    userId :List[int]
    iltId :int
    rockId :int
    rockOwnerId:int
    