from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.exceptions.customException import CustomException
from app.models import  MdlUsers

class loginService:
    def check_login(self, userName:str, password:str, db:Session):
        user_re = db.query(MdlUsers).filter(MdlUsers.email==userName).one_or_none()
        if user_re is None: 
            1/0
            raise CustomException(404, "user name not found")

        actual_password = user_re.password
        if password.strip() == actual_password:
            return {
                        "userId": user_re.id,	
                        "emailId":user_re.email,
                        "firstName": user_re.fname,
                        "lastName": user_re.lname,
                        "roleId": user_re.role_id
                    }
        else: 
            return {
                            "confirmMessageID": "string",
                            "statusCode": 200,
                            "userMessage": "password doesn't match"
                        }