from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.exceptions.customException import CustomException
from app.models import  MdlUsers
from app.exceptions.customException import CustomException
import bcrypt

def verify_password(input_password, hashed_password, salt):
    hashed_input_password = bcrypt.hashpw(
        input_password.encode('utf-8'), salt.encode('utf-8'))
    return hashed_input_password == hashed_password.encode('utf-8')

class loginService:
    def check_login(self, userName:str, password:str, db:Session, is_reset=False):

        if is_reset:
            return {
                "statusCode": 200,
                "userMessage": "Please contact your administrator for reseting password!"
            }
        user_re = db.query(MdlUsers).filter(MdlUsers.email==userName).one_or_none()
        if user_re is None:     
            raise CustomException(400, "Invaild userName/password")

        if verify_password(input_password=password, hashed_password=user_re.password, salt=user_re.salt_key):
            return {
                        "userId": user_re.id,	
                        "emailId":user_re.email,
                        "firstName": user_re.fname,
                        "lastName": user_re.lname,
                        "roleId": user_re.role_id
                    }
        else: 
            raise CustomException(400, "Invaild userName/password")