from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class member(BaseModel):
    id: int

class Ilt(BaseModel):
    title: str=""
    description: str=""
    schoolId: int=0
    # ownerId:int
    # member_ids: list[member]