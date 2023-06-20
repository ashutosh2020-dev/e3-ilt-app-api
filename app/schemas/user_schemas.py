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
