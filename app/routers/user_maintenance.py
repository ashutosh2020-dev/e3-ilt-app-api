from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.get("/api/v1/users/")
def fn_read_users(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user(user_id, db =db)


@router.post("/api/v1/users/")
def fn_create_user(UserId: int, fname: str, lname: str, email: str, number: str, \
                   password: str, is_active: bool, role_id: int, db: Session = Depends(get_db)):
    return user_service.create_user(parent_user_id=UserId, fname=fname, lname=lname, email=email, number=number, 
                                         password=password, is_active=is_active, role_id=role_id, db=db)
    
@router.post("/api/v1/users/{id}")
def fn_update_user(logged_user_id: int, user_id:int, fname: str, lname: str, email: str, number: str, \
                   password: str, is_active: bool, role_id: int, db: Session = Depends(get_db)):
    return user_service.update_user(logged_user_id, user_id, fname, lname, email, number, password, is_active, role_id, db=db)

@router.post("/api/v1/users/{id}/delete")
def fn_delete_user(user_id: int, db: Session = Depends(get_db)):
    return "functionality is commented"#user_service.delete_user(user_id, db=db)