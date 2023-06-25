from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.user_service import UserService
from app.schemas.user_schemas import UserRequest
router = APIRouter()
user_service = UserService()

@router.get("/api/v1/users/")
def fn_read_users(UserId: int=Header(convert_underscores=False),  db: Session = Depends(get_db)):
    return user_service.get_user(UserId, db =db)

@router.get("/api/v1/users/search")
def fn_read_users(keyword:str, UserId: int=Header(convert_underscores=False),  db: Session = Depends(get_db)):
    return user_service.search_user(UserId, keyword, db =db)


@router.post("/api/v1/users/")
def fn_create_user(user:UserRequest, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return user_service.create_user(parent_user_id=UserId,
                                    fname=user.firstName, 
                                    lname=user.lastName,
                                    email=user.emailId,
                                    number=user.phoneNumber, 
                                    password=user.password, 
                                    is_active=user.active,
                                    role_id=user.roleId,
                                    db=db)
    
@router.post("/api/v1/users/{id}")
def fn_update_user(id:int, user:UserRequest, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return user_service.update_user(user_id = UserId, 
                                    id = id,
                                    fname=user.firstName, 
                                    lname=user.lastName,
                                    email=user.emailId, 
                                    number=user.phoneNumber, 
                                    password=user.password, 
                                    is_active=user.active,
                                    role_id=user.roleId,
                                    db=db)


@router.post("/api/v1/users/{id}/delete")
def fn_delete_user(UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return "functionality is commented"#user_service.delete_user(UserId, db=db)