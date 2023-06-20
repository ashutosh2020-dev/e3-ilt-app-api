from pydantic import BaseModel

class User(BaseModel):
    fname: str
    lname: str
    email: str
    number: str
    password: str
    is_active: bool
    role_id: int

class school(BaseModel):
    name: str
    location: str
    district: str

class Role(BaseModel):
    role_name: str
    roleDescription: str

class priority(BaseModel):
    name: str
    description: str