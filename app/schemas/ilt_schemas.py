from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class member(BaseModel):
    id: int


class Createilt(BaseModel):
    title: str
    description: str
    schoolId: int
    owner_id:int
    memberIds: List[int]

class Ilt(BaseModel):
    iltId: Optional[int] = None
    title: str=""
    description: str=""
    schoolId: int=0
    ownerId:int
    memberIds: list[int]