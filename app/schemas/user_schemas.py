from pydantic import BaseModel

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
    firstName: str
    lastName: str
    emailId: str
    phoneNumber: str
    password: str
    active: bool
    roleId: int

class loginCredential(BaseModel):
    userName:str
    password:str


class UserAccount():
    def __init__(self, userId: int, firstName: str, lastName: str, roleId: int):
        self.userId = userId
        self.firstName = firstName
        self.lastName = lastName
        self.roleId = roleId