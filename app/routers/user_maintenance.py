from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.user_service import UserService
from app.schemas.user_schemas import UserRequest, UpdateUserRequest, UpdateUserPasswordRequest
router = APIRouter()
user_service = UserService()

@router.get("/api/v1/users/")
def fn_read_users(keyword:str = "", UserId: int=Header(convert_underscores=False), minRole=0,  db: Session = Depends(get_db)):
    if not keyword:
        return user_service.get_user(UserId, db =db)
    else:
        return user_service.search_user(UserId, keyword=keyword, min_role=minRole, db=db)
    
@router.get("/api/v1/users/{userId}")
def fn_read_users(userId: int,  db: Session = Depends(get_db)):
    return user_service.get_single_user(userId, db =db)

@router.get("/api/v1/users/{userId}/districts")
def fn_read_users_districts(userId: int,  db: Session = Depends(get_db)):
    return user_service.get_districts(userId, db =db)

@router.get("/api/v1/users/districts/{districtId}/schools")
def fn_read_users_schools(districtId: int,  db: Session = Depends(get_db)):
    return user_service.get_schools(districtId, db =db)

@router.get("/api/v1/users/districts/{districtId}/ilts")
def fn_read_users_district_ilts(districtId: int,  db: Session = Depends(get_db)):
    return user_service.get_district_ilts(districtId, db =db)

@router.post("/api/v1/users/")
async def fn_create_user(user:UserRequest, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return user_service.create_user(parent_user_id=UserId,
                                    fname=user.firstName, 
                                    lname=user.lastName,
                                    email=user.emailId,
                                    number=user.phoneNumber, 
                                    password=user.password, 
                                    is_active=user.active,
                                    role_id=user.roleId,
                                    districts=user.districts,
                                    db=db)
    
@router.post("/api/v1/users/{id}")
def fn_update_user(id:int, user:UpdateUserRequest, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return user_service.update_user(user_id = UserId, 
                                    id = id,
                                    fname=user.firstName, 
                                    lname=user.lastName,
                                    email=user.emailId, 
                                    number=user.phoneNumber, 
                                    password=user.password, 
                                    is_active=user.active,
                                    role_id=user.roleId,
                                    districts=user.districts,
                                    db=db)
@router.post("/api/v1/users/{id}/password")
def fn_update_user_password(id:int, user:UpdateUserPasswordRequest, UserId: int=Header(convert_underscores=False), 
                   db: Session = Depends(get_db)):
   return user_service.update_password(old_password= user.oldPassword, 
                                       new_password = user.newPassword,
                                       loginUserId = UserId, 
                                       id = id,
                                       db=db)


@router.post("/api/v1/users/{emailId}/reset/password")
def fn_reset_user_password(emailId: str, 
                            db: Session = Depends(get_db)):
   
   return user_service.reset_password(email_id=emailId, db = db)

@router.post("/api/v1/users/{id}/delete")
def fn_delete_user(UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return "functionality is commented" #user_service.delete_user(UserId, db=db)