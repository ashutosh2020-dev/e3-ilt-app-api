from sqlalchemy.orm import Session
from app.models import MdlRoles, MdlUsers, MdlSchools, MdlPriorities, MdlDistrict, MdlDistrictMember
import sys
from app.exceptions.customException import CustomException
import bcrypt

def hash_password(password, salt_rounds=12):
    salt = bcrypt.gensalt(salt_rounds)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return [hashed_password.decode('utf-8'), salt.decode('utf-8')]


def verify_password(input_password, hashed_password, salt):
    hashed_input_password = bcrypt.hashpw(
        input_password.encode('utf-8'), salt.encode('utf-8'))
    return hashed_input_password == hashed_password.encode('utf-8')

class Create_otherService:
    def create_root_user(self,  fname, lname, email, number, password, is_active, role_id, districts, db: Session):

        email = email.strip().lower()
        password = password.strip()
        fname = fname.strip()
        lname = lname.strip()

        # check_parent_id = db.query(MdlUsers).filter(
        #     MdlUsers.id == parent_user_id).one_or_none()
        # if check_parent_id is None:
        #     raise CustomException(400,  "UserId not found")
        check_role_id = db.query(MdlRoles).filter(
            MdlRoles.id == role_id).one_or_none()
        if check_role_id is None:
            raise CustomException(400,  "role not found")
        # email check
        check_user_detail = (db.query(MdlUsers)
                        .filter(MdlUsers.email == email)
                        .one_or_none())
        if check_user_detail is not None:
            raise CustomException(400,  "This email id already exists, Please change your email id.")
        # number
        # check_user_detail = (db.query(MdlUsers)
        #                 .filter(MdlUsers.number == number.strip())
        #                 .one_or_none())
        # if check_user_detail is not None:
        #     raise CustomException(400,  "This phone number already exists, Please share your another number.")
        # check roleId
        # if role_id >= check_parent_id.role_id and (check_parent_id.role_id !=4):
        #     raise CustomException(
        #         400,  "Please downgrade the role to create user")
        # if len(districts) == 0 and check_parent_id.role_id !=4:
        #     raise CustomException(400,  "Please enter district")
        
        # create district_list
        district_list = []
        #check roleid then, roleid>=3 multpile district allow, if <3 only 1 district
        # if role_id<=2:
        #     if len(districts)!=1 and role_id==1:
        #         raise CustomException(400,  "Please enter only one district")
            
        #     district_list =  [re.district_id for re in db.query(MdlDistrictMember).filter(MdlDistrictMember.user_id == check_parent_id.id).all()]
        #     for d in districts:
        #         if d not in district_list:
        #             raise CustomException(400,  "You can not create user in this district, Please change the district.")
                
        # if role_id>=3:
        #     district_list =  [re.district_id for re in db.query(MdlDistrictMember).filter(MdlDistrictMember.user_id == check_parent_id.id).all()]
        #     for d in districts:
        #         if d not in district_list:
        #             raise CustomException(400,  "You can not create user in this district, Please change the district.")

            #district_list.extend([dis.name for dis in db.query(MdlDistrict).all()]) #cal parent access area & append                
        if role_id ==4 and len(districts)==0:
            districts = [re.id for re in db.query(MdlDistrict).all()]
        hashPassword, saltKey = hash_password(password)
        if districts:
            db_user = MdlUsers(fname=fname, lname=lname, email=email,
                               password=hashPassword, salt_key=saltKey, is_active=is_active, role_id=role_id, parent_user_id=0)
            if number:
                db_user.number=number
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        
            for d_id in districts:
                db_distric_user = MdlDistrictMember(district_id= d_id, user_id=db_user.id) 
                db.add(db_distric_user)
                db.commit()
                db.refresh(db_distric_user)     
            return {

                "statusCode": 200,
                "userMessage": "User has created successfully"
            }
        else:
            raise CustomException(400,  "Please ")

    def create_schools(self, name, location, districtId, db:Session):
        check_district = db.query(MdlDistrict).filter(MdlDistrict.id==districtId).one_or_none()
        if check_district is None:
            raise CustomException(400,  "This district is exist")
        db_school = MdlSchools(name=name, location=location, district=districtId)
        db.add(db_school)
        db.commit()
        db.refresh(db_school) 
        return {
                
                "statusCode": 200,
                "userMessage": "school has created successfully."
                }
        
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
            db_priority = MdlPriorities(name=name, description=description)
            db.add(db_priority)
            db.commit()
            db.refresh(db_priority)
            return {
                   
                    "statusCode": 200,
                    "userMessage": "priority has created."
                    }

    def create_district(self, name, db:Session):
        db_district = MdlDistrict(name=name)
        db.add(db_district)
        db.commit()
        db.refresh(db_district)
        
        all_director = [re.id for re in db.query(MdlUsers).filter(MdlUsers.role_id==4).all()]
        if all_director:
            for  director_id in  all_director:
                db_distric_user = MdlDistrictMember(
                            district_id=db_district.id, user_id=director_id)
                db.add(db_distric_user)
                db.commit()
                db.refresh(db_distric_user)


        return {
                   
                    "statusCode": 200,
                    "userMessage": "district has been created."
                    }