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