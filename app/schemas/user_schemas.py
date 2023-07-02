from pydantic import BaseModel
from typing import List, Optional


class UserRequest(BaseModel):
    # userId: int
    firstName: str
    lastName: str
    emailId: str
    phoneNumber: str
    password: str
    active: bool
    roleId: int

class UpdateUserRequest(BaseModel):
    # userId: int
    firstName: Optional[str]=""
    lastName: Optional[str]=""
    emailId: Optional[str]=""
    phoneNumber: Optional[str]=""
    password: Optional[str]="12345"
    active: Optional[bool]=None
    roleId: Optional[int]=0
    

class loginCredential(BaseModel):
    userName:str
    password:str


class UserAccount():
    def __init__(self, userId: int, firstName: str, lastName: str, roleId: int, emailId: str):
        self.userId = userId
        self.firstName = firstName
        self.lastName = lastName
        self.roleId = roleId
        self.emailId = emailId