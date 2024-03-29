from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import MdlUsers, MdlRoles, MdlIlts, MdlDistrict, MdlDistrictMember, MdlSchools
from sqlalchemy.orm.exc import NoResultFound
import sys, re
from app.schemas.ilt_schemas import Ilt_scheema
from app.exceptions.customException import CustomException
from app.schemas.user_schemas import UserAccount
from app.services.utils import get_user_info
import bcrypt
import random
import string

def hash_password(password, salt_rounds=12):
    salt = bcrypt.gensalt(salt_rounds)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return [hashed_password.decode('utf-8'), salt.decode('utf-8')]


def verify_password(input_password, hashed_password, salt):
    hashed_input_password = bcrypt.hashpw(
        input_password.encode('utf-8'), salt.encode('utf-8'))
    return hashed_input_password == hashed_password.encode('utf-8')

def generate_random_alphanumeric_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

class UserService:
    def get_user(self, user_id: int, db: Session):
        u_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if u_record is None:
            raise CustomException(404, "user records not found.")

        elif u_record.role_id == 1:
            return [{"userId": u_record.id,
                     "firstName": u_record.fname,
                     "lastName": u_record.lname,
                     "emailId": u_record.email,
                     "phoneNumber": u_record.number,
                     "password": "*******",
                     "active": u_record.is_active,
                     "roleId": u_record.role_id,
                     "assignedTo": get_user_info(db=db, userId=u_record.parent_user_id)}]

        elif u_record.role_id == 2 or u_record.role_id == 3:
            users_list = []
            user_query = db.query(MdlUsers).filter(
                MdlUsers.parent_user_id == user_id).order_by(MdlUsers.id)
            associated_users_record = user_query.all()
            for user_record in associated_users_record:
                users_list.append({"userId": user_record.id,
                                   "firstName": user_record.fname,
                                   "lastName": user_record.lname,
                                   "emailId": user_record.email,
                                   "phoneNumber": user_record.number,
                                   "password": "*******",
                                   "active": user_record.is_active,
                                   "roleId": user_record.role_id,
                                   "assignedTo": get_user_info(db=db, userId=u_record.parent_user_id)})
            return users_list
        elif u_record.role_id == 4:
            users_list = []
            user_query = db.query(MdlUsers)
            associated_users_record = [{"userId": record.id,
                                        "firstName": record.fname,
                                        "lastName": record.lname,
                                        "emailId": record.email,
                                        "phoneNumber": record.number,
                                        "password": "*******",
                                        "active": record.is_active,
                                        "roleId": record.role_id,
                                        "assignedTo": get_user_info(db=db, userId=u_record.parent_user_id)
                                        } for record in user_query.order_by(MdlUsers.id).all()]
            return associated_users_record

    def get_single_user(self, user_id: int, db: Session):
        u_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if u_record is None:
            raise CustomException(404, "user records not found.")

        district_list = []
        district_record = db.query(MdlDistrictMember).filter(
            MdlDistrictMember.user_id == user_id).all()
        for district_map_re in district_record:
            district_re = db.query(MdlDistrict).filter(
                MdlDistrict.id == district_map_re.district_id).one_or_none()
            district_list.append(district_re.id)

        return {"userId": u_record.id,
                "firstName": u_record.fname,
                "lastName": u_record.lname,
                "emailId": u_record.email,
                "phoneNumber": u_record.number,
                "password": "*******",
                "active": u_record.is_active,
                "roleId": u_record.role_id,
                "assignedTo": get_user_info(db=db, userId=u_record.parent_user_id),
                "districts": district_list}

    def search_user(self, user_id: int, keyword: str, db: Session, min_role=0):
        u_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if u_record is None:
            raise CustomException(404, "User records not found.")
        
        elif u_record.role_id != 1:
            district_id_list = [re.district_id 
                                for re in db.query(MdlDistrictMember)
                                            .filter(MdlDistrictMember.user_id==user_id)
                                            .all()]
            user_query = (
                            db.query(MdlUsers)
                            .join(MdlDistrictMember, MdlUsers.id == MdlDistrictMember.user_id)
                        )
            if keyword:
                user_query = user_query.filter(MdlDistrictMember.district_id.in_(district_id_list),
                                               MdlUsers.role_id>=min_role,
                                               and_(MdlUsers.fname.ilike(f"%{keyword}%")
                                               | MdlUsers.lname.ilike(f"%{keyword}%")
                                               | MdlUsers.email.ilike(f"%{keyword}%")))
            associated_users_record = [UserAccount(record.id, record.fname, record.lname, record.role_id, record.email)
                                       for record in user_query.order_by(MdlUsers.id).all()]
            return associated_users_record
        else:
            raise CustomException(
                404, "This user can not see the others user details.")

    def get_districts(self, user_id: int, db: Session):
        # check userId
        u_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if u_record is None:
            raise CustomException(404, "User records not found.")

        district_list = []
        district_record_all = db.query(MdlDistrict).all()
        user_district_ids = [d_id for d_id, in db.query(MdlDistrictMember.district_id).filter(
            MdlDistrictMember.user_id == user_id).all()]
        
        for district_re in district_record_all:
            district_list.append({
                "value": district_re.id,
                "label": district_re.name,
                "isAssigned": True if district_re.id in user_district_ids else False
            })
        return district_list


    def get_district_ilts(self, districtId, db:Session):
         # check userId
        d_record = db.query(MdlDistrict).filter(
            MdlDistrict.id == districtId).one_or_none()
        if d_record is None:
            raise CustomException(404, "records not found.")
        list_d_ilts = []
        schoolIdList = db.query(MdlSchools.id,).filter(
            MdlSchools.district == districtId).all()
        print(schoolIdList)
        for schoolId, in schoolIdList:
            ilts_re = db.query(MdlIlts).filter(MdlIlts.school_id==schoolId).all()    
            list_ilts = [Ilt_scheema(ilt_re) for ilt_re in ilts_re]
            list_d_ilts.extend(list_ilts)
        return list_d_ilts

    def get_schools(self, districtId: int, db: Session):
        d_record = db.query(MdlDistrict).filter(
            MdlDistrict.id == districtId).one_or_none()
        if d_record is None:
            raise CustomException(404, "District records not found.")

        school_list = []
        district_record = db.query(MdlSchools).filter(
            MdlSchools.district == districtId).all()
        for school_re in district_record:
            school_list.append({
                "value": school_re.id,
                "label": school_re.name
            })
        return school_list

    def create_user(self, user_id, assigned_to, fname, lname, email, number, password, is_active, role_id, districts, db: Session):
        email = email.strip().lower()
        fname = fname.strip()
        lname = lname.strip()

        logged_user_re = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        if logged_user_re is None:
            raise CustomException(400,  "UserId not found")
        assigned_user_re = db.query(MdlUsers).filter(MdlUsers.id == assigned_to).one_or_none()
        if assigned_user_re is None:
            raise CustomException(400,  "Invalid 'assigned to' user")
        
        if role_id > assigned_user_re.role_id: 
            raise CustomException(400,  "Invalid 'assigned to' user, Please downgrade the Role  of user or change the 'assignd to' user ")
        
        a_district_list = [d_id for d_id, in db.query(MdlDistrictMember.district_id)
                                               .filter(MdlDistrictMember.user_id == assigned_user_re.id)
                                               .all()]
        if any(d not in a_district_list for d in districts) and len(districts) != 0:
            raise CustomException(
                400,  "Access Denied: Some districts are outside of your authorized area. Please update your district selection.")
        
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise CustomException(400,  "Invalid Email format")
        
        if db.query(MdlRoles).filter(MdlRoles.id == role_id).one_or_none() is None:
            raise CustomException(400,  "role not found")
        # email check
        if db.query(MdlUsers).filter(MdlUsers.email == email).one_or_none() is not None:
            raise CustomException(
                400,  "Email already exists. Please choose a different email address.")
        # check roleId
        if role_id >= logged_user_re.role_id and (logged_user_re.role_id != 4):
            raise CustomException(
                400,  "Please downgrade the role to create user")
        if len(districts) == 0 and logged_user_re.role_id != 4:
            raise CustomException(400,  "Please choose district")

        # validate roleId then, roleid>=3 - multpile district allow, if <=2 -only 1 district
        district_list = [d_id for d_id, in db.query(MdlDistrictMember.district_id)
                                                    .filter(MdlDistrictMember.user_id == logged_user_re.id)
                                                    .all()]
        if role_id <= 2:
            if len(districts) != 1:
                raise CustomException(400,  "Please enter only one district")
        if any(d not in district_list for d in districts) and len(districts) != 0:
            raise CustomException(400, "You can not create a user in this district. Please change the district.")
        if role_id == 4 and len(districts) == 0:
            districts = district_list
        
        hashPassword, saltKey = hash_password(password)
       
        db_user = MdlUsers(fname=fname, lname=lname, email=email,
                            password=hashPassword, salt_key=saltKey,
                            is_active=is_active, role_id=role_id, parent_user_id=assigned_to)
        if number:
            db_user.number = number
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        for d_id in districts:
            db_distric_user = MdlDistrictMember(
                district_id=d_id, user_id=db_user.id)
            db.add(db_distric_user)
            db.commit()
            db.refresh(db_distric_user)
        return {
            "statusCode": 200,
            "userMessage": "User has created successfully"
        }
        

    def update_user(self, user_id: int, id: int, fname, lname, email, number, password, is_active, districts, role_id, assigned_to, db: Session):
        
        fname = fname.strip()
        lname = lname.strip()
        user_id_re = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        db_user = db.query(MdlUsers).filter(MdlUsers.id == id).one()
        if user_id_re is None:
            raise CustomException(404,  "Record not found.")
        if assigned_to:
            assigned_user_re = db.query(MdlUsers).filter(MdlUsers.id == assigned_to).one_or_none()
            user_districts = [re.district_id for re in db.query(MdlDistrictMember)
                                                            .filter(MdlDistrictMember.user_id == id)
                                                            .all()] if len(districts)==0 else districts
            if assigned_user_re is None:
                raise CustomException(400,  "Invalid 'assigned to' user")

            if db_user.role_id > assigned_user_re.role_id:
                raise CustomException(
                    400,  "Invalid 'assigned to' user, Please downgrade the Role  of user or change the 'assignd to' user ")

            a_district_list = [d_id for d_id, in db.query(MdlDistrictMember.district_id)
                                                .filter(MdlDistrictMember.user_id == assigned_user_re.id)
                                                .all()]
            if any(d not in a_district_list for d in user_districts) and len(user_districts) != 0:
                raise CustomException(
                    400,  "Access Denied: Some districts are outside of your authorized area. Please update your district selection.")
        check_parent_record = db.query(MdlUsers).filter(
            MdlUsers.parent_user_id == id).all()
        check_iltOwner_record = db.query(
            MdlIlts).filter(MdlIlts.owner_id == id).all()
        if email:
            email = email.strip().lower()
            is_valid_email = re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)
            if not is_valid_email:
                raise CustomException(400,  "Invalid Email format")
            # check is email duplicate
            if db_user.email != email:
                check_user_detail = (db.query(MdlUsers)
                                    .filter(MdlUsers.email == email)
                                    .one_or_none())
                if check_user_detail is not None:
                    raise CustomException(
                        400,  "This email id already exists, Please change your email id.")

        if role_id:
            check_role_id = db.query(MdlRoles).filter(
                MdlRoles.id == role_id).one_or_none()
            if check_role_id is None:
                raise CustomException(404,  "Record not found wrt roleId.")
            if (db_user.parent_user_id != user_id) and (user_id_re.role_id < 3):
                db.close()
                raise CustomException(
                    400,  "you are not allowed to modify this user's details")
            if role_id >= user_id_re.role_id and user_id_re.role_id != 4:
                raise CustomException(
                    400,  "This logged-in user can not modify user's details, please change/downgrade the role id")
            if role_id < db_user.role_id:
                # check if he is an owner of ilt, or parent of any ilt,
                if check_iltOwner_record or check_parent_record:
                    raise CustomException(
                        400,  "Can not downgrade the role of user. he is either owner/parent of ilts/users")
            db_user.role_id = role_id

        if (is_active == False) and (db_user.is_active == True):
            if check_iltOwner_record or check_parent_record:
                if check_iltOwner_record and check_parent_record:
                    raise CustomException(
                        400,  "Cannot deactivate user. This user is an owner in Ilt and a parent to other users.")
                elif check_parent_record:
                    raise CustomException(
                        400,  "Cannot deactivate user. This user is a parent to other users.")
                else:
                    raise CustomException(
                        400,  "Cannot deactivate user. This user is an owner in Ilt.")
            else:
                pass
        
        if fname:
            db_user.fname = fname
        if lname:
            db_user.lname = lname
        if email:
            db_user.email = email
        if number:
            db_user.number = number
        if is_active is not None:
            db_user.is_active = is_active
        if assigned_to:
            db_user.parent_user_id = assigned_to
        db.commit()
        db.refresh(db_user)
        if districts:
            # update district
            old_districts = set([re.district_id for re in db.query(MdlDistrictMember).filter(MdlDistrictMember.user_id==id).all()])
            input_new_district = set(districts)
            new_districts_list = input_new_district - old_districts
            remove_districts_list = old_districts - input_new_district
            # existing_districts_list = old_districts.intersection(input_new_district)
            all_district_list = old_districts.union(input_new_district)
            for dis_id in all_district_list:
                if dis_id in new_districts_list:
                    distr_map_record= MdlDistrictMember(district_id=dis_id, user_id=id)
                    db.add(distr_map_record)
                    db.commit()
                elif dis_id in remove_districts_list:
                    distr_map_record = db.query(MdlDistrictMember).filter(MdlDistrictMember.district_id==dis_id,
                                                                        MdlDistrictMember.user_id==id).one()
                    db.delete(distr_map_record)
                    db.commit()
                else:
                    pass

        return {
            "statusCode": 200,
            "userMessage": "User Updated successfully."
        }

    def update_all(self, user_id: int, id: int, fname, lname, email, number, password, is_active, role_id, db: Session):
        user_list = db.query(MdlUsers).all()
        for db_user in user_list:
            db_user.is_active = True
            db.commit()
            db.refresh(db_user)
        print("done")
        return "done"

    def delete_user(self, user_id: int, db: Session):

        return {
            "statusCode": 200,
            "userMessage": "...."
        }

    def update_password(self, loginUserId, id, old_password, new_password, db:Session):

        db_user_re = (db.query(MdlUsers).filter(MdlUsers.id == id).one_or_none())
        if db_user_re is None:
            raise CustomException(404,  "Record not found.")
        if db.query(MdlUsers.password).filter(MdlUsers.id == loginUserId).one_or_none() is None:
            raise CustomException(404,  "Record not found.")
        if not db_user_re.salt_key:
            raise CustomException(404,  "Cannot change this password. Please contact the administrator.")
        existing_password, saltKey = db_user_re.password, db_user_re.salt_key
        is_match = verify_password(input_password=old_password,
                                   hashed_password=existing_password,
                                   salt=saltKey)
        if is_match:
            hpass, saltKey = hash_password(new_password)
            db_user_re.password = hpass
            db_user_re.salt_key = saltKey
            db.add(db_user_re)
            db.commit()
        else:
            raise CustomException(404, "Incorrect Password!")
        return {
            "statusCode": 200,
            "userMessage": "Password updated successfully"
        }
        
    def reset_password(self, email_id, db):
        emailId = email_id.strip()
        db_user_re = db.query(MdlUsers).filter(MdlUsers.email ==emailId).one_or_none()
        if db_user_re is None:
            raise CustomException(404, "Invalid Email id!")
        newPassword = generate_random_alphanumeric_string(length=16)
        hpass, salt_key = hash_password(password=newPassword)

        db_user_re.password = hpass
        db_user_re.salt_key = salt_key
        db.commit()
        db.refresh(db_user_re)

        return {
            "statusCode": 200,
            "userMessage": f"Password has been reset to default one '{newPassword}'. Please update password once login!"
        }
