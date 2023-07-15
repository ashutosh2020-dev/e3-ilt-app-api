from pydantic import BaseModel
from typing import List, Optional


class User(BaseModel):
    # userId: int
    firstName: str
    lastName: str
    emailId: str
    phoneNumber: Optional[str]=""
    password: str
    active: bool
    roleId: int
    districts:Optional[List[int]]=[]


class school(BaseModel):
    name: str
    location: str
    districtId: int

class Role(BaseModel):
    role_name: str
    roleDescription: str

class priority(BaseModel):
    name: str
    description: str

class district(BaseModel):
    name:str