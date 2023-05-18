from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()

@router.get("/api/v1/users/{id}")
def fn_read_users(user_id: int, db: Session = Depends(get_db)):
    user_record= user_service.get_user(user_id, db =db)
    print(user_record)
    if user_record:
        return {
                    "userId": user_record.id,
                    "firstName": user_record.fname,
                    "lastName": user_record.lname,
                    "emaildId": user_record.email,
                    "phoneNumber": user_record.number,
                    "password": user_record.password,
                    "active": user_record.is_active,
                    "roleId": user_record.role_id
                }
    else:
        return {"records":"not found"}

@router.post("/api/v1/users/")
def fn_create_user(UserId: int, fname: str, lname: str, email: str, number: str, \
                   password: str, is_active: bool, role_id: int, memberIds: list, db: Session = Depends(get_db)):
    up_status = user_service.create_user(UserId, fname, lname, email, number, 
                                         password, is_active, role_id, db=db)
    if up_status:
       return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "created successfully"
                }
    else:
        return {
                "confirmMessageID": "string",
                "statusCode": 404,
                "userMessage": "unable to create"
                }

@router.post("/api/v1/users/{id}")
def fn_update_user(user_id: int, fname: str, lname: str, email: str, number: str, \
                   password: str, is_active: bool, role_id: int, db: Session = Depends(get_db)):
    status = user_service.update_user(user_id, fname, lname, email, number, password, is_active, role_id, db=db)
    if status:
        return {
            "confirmMessageID": "string",
            "statusCode": 200,
            "userMessage": "user updated successfully"
            }
    else:
        return {
        "confirmMessageID": "string",
        "statusCode": 400,
        "userMessage": "failed"
        }