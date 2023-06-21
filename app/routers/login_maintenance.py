from fastapi import APIRouter, Depends, Body, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models import MdlIlts, MdlIltMembers, MdlUsers, MdlSchools

router = APIRouter()


@router.get("/api/v1/login")
def login( password:str, UserId: int=Header(convert_underscores=False), db:Session=Depends(get_db)):
    user_re = db.query(MdlUsers).filter(MdlUsers.id==UserId).one_or_none()
    if user_re is None: 
        return {
                        "confirmMessageID": "string",
                        "statusCode": 404,
                        "userMessage": "User did not found"
                    }
    actual_password = user_re.password   
    if password == actual_password:
        return {
                        "confirmMessageID": "string",
                        "statusCode": 200,
                        "userMessage": "user has successfully login"
                    }
    else: 
        return {
                        "confirmMessageID": "string",
                        "statusCode": 200,
                        "userMessage": "password in not matching"
                    }