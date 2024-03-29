from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class member(BaseModel):
    id: int

class Ilt(BaseModel):
    iltId: Optional[int] = 0
    title: Optional[str] =""
    description: Optional[str]=""
    schoolId: Optional[int]=0
    ownerId:Optional[int]=0
    memberIds: Optional[list[int]]=[]

class Ilt_scheema:
    def __init__(self, record) -> None:
        self.iltId: Optional[int] = record.id
        self.title: Optional[str] = record.title
        self.description: Optional[str] = record.description
        self.schoolId: Optional[int] = record.school_id
        self.ownerId: Optional[int] = record.owner_id
        self.memberIds: List[int] = []