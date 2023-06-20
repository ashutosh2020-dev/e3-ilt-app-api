from pydantic import BaseModel
from datetime import datetime

class MeetingData(BaseModel):
    scheduledStartDate: datetime
    meetingStart: datetime
    meetingEnd: datetime
    location: str

class rockData(BaseModel):
    ilt_id:int
    name:str
    description:str

class rockData_map(BaseModel):
    user_id :int
    Ilt_id :int
    rock_id :int