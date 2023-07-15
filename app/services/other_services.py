from sqlalchemy.orm import Session
from app.models import MdlRoles, MdlUsers, MdlSchools, MdlPriorities
import sys
from app.exceptions.customException import CustomException

class Create_otherService:
    def create_root_user(self, fname, lname, email, number, password, is_active, role_id, db: Session):
        try:
            db_user = MdlUsers(fname=fname, lname=lname, email=email, number=number, \
                            password=password, is_active=is_active, role_id=role_id, parent_user_id= 0)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            record = db.query(MdlUsers).get(db_user.id)
            if record:
                record.parent_user_id=db_user.id
                db.commit()
            db.close()
            return {
               
                "statusCode": 200,
                "userMessage": "root user has created successfully"
                }
        except Exception as e:
            raise CustomException(400,  f"unable to create the record : {e}")
    def create_schools(self, name, location, district, db:Session):
        try:
            db_school = MdlSchools(name=name, location=location, district=district)
            db.add(db_school)
            db.commit()
            db.refresh(db_school) 
            return {
                   
                    "statusCode": 200,
                    "userMessage": "school has created successfully."
                    }
        except Exception as e:
            raise CustomException(500,  f"unable to create school, this school's name already exist.{e}")
    
    def create_roles(self, role_name:str, roleDescription:str, db:Session):
        db_role = MdlRoles(name=role_name, description=roleDescription)
        db.add(db_role)
        db.commit()
        db.refresh(db_role) 
        return {
               
                "statusCode": 200,
                "userMessage": "role has created successfully."
                }

    def update_roles(self, role_name:str, roleDescription:str, db:Session):
        member = ["ILT Member", "ILT Facilitator", "Project Leader"]
        for i in range(1,4):
            db_record = db.query(MdlRoles).get(i)
            db_record.name =member[i-1] 
            db.commit()
            db.refresh(db_record)
            print(db_record.name)

    def create_priority(self, name, description, db:Session):
        try:
            db_priority = MdlPriorities(name=name, description=description)
            db.add(db_priority)
            db.commit()
            db.refresh(db_priority)

            return {
                   
                    "statusCode": 200,
                    "userMessage": "priority has created."
                    }
        except Exception as e:
             raise CustomException(500, f"unable to process your request. error - {e}")
