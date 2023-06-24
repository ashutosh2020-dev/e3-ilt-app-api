from fastapi import APIRouter, Depends, Body, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.user_schemas import loginCredential
from app.services.login_service import loginService 
router = APIRouter()
login_service = loginService()

@router.post("/api/v1/login")
def login( creadential:loginCredential, db:Session=Depends(get_db)):
    return login_service.check_login(userName=creadential.userName, password=creadential.password, db= db)