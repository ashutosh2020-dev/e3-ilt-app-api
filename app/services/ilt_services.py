from sqlalchemy.orm import Session
from app.models import MdlIlts, MdlIltMembers, MdlUsers, MdlSchools, MdlMeetings, MdlIltMeetings, MdlRocks, MdlIlt_rocks
from app.schemas.ilt_schemas import Ilt
from app.services.ilt_meeting_response_service import IltMeetingResponceService
from datetime import datetime, timezone
from app.exceptions.customException import CustomException
from sqlalchemy import and_, func


class IltService:
    def get_Ilts_list(self, user_id: int, db: Session):
        ilt_list = []
        list_ilts = []
        user_id_list = []
        logged_user_record = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        if logged_user_record is None: 
            raise CustomException(400,  "User invalid") 
        
        # role<=2, append all ilt wrt userid
        if logged_user_record.role_id<=2:
            user_id_list.append(user_id)
            
        elif logged_user_record.role_id==3:
            user_id_list.append(user_id)
            #extend child facilitator
            user_id_list.extend([u_re.id 
                                 for u_re in db.query(MdlUsers).filter(MdlUsers.parent_user_id==user_id).all()])
        elif logged_user_record.role_id==4:
            user_id_list.append(user_id)
            #extract child project manager id
            child_p_list = [u_re.id 
                                 for u_re in db.query(MdlUsers).filter(MdlUsers.parent_user_id==user_id).all()]
            user_id_list.extend(child_p_list)
            for id in child_p_list:
                # extract child facilitator id for each
                child_f_list = [u_re.id 
                                 for u_re in db.query(MdlUsers).filter(MdlUsers.parent_user_id==id).all()]
                user_id_list.extend(child_f_list)

        elif logged_user_record.role_id>4:
            user_id_list.append(user_id)
            #extract child director id
            child_p_list = [u_re.id 
                                 for u_re in db.query(MdlUsers).filter(MdlUsers.parent_user_id==user_id).all()]
            user_id_list.extend(child_p_list)
            for id in child_p_list:
                # extract child project manager id for each
                child_f_list = [u_re.id 
                                 for u_re in db.query(MdlUsers).filter(MdlUsers.parent_user_id==id).all()]
                user_id_list.extend(child_f_list)

        if logged_user_record.role_id<=2:
            list_ilts.extend([record.ilt_id for record in db.query(
                                            MdlIltMembers).filter(MdlIltMembers.member_id == uid).all()])
        elif logged_user_record.role_id>=3:
            for  uid in user_id_list:
                list_ilts.extend([record.id for record in db.query(
                    MdlIlts).filter(MdlIlts.owner_id == uid).all()])
        
        if list_ilts:
            list_ilts  = list(set(list_ilts))
            for x in list_ilts:
                latestMeetingId = 0
                status = 0
                ilt_record = db.query(MdlIlts).filter(MdlIlts.id == x).first()
                ilt_owner_record = db.query(MdlUsers).filter(
                    MdlUsers.id == ilt_record.owner_id).first()
                owner_name = ilt_owner_record.fname+" "+ilt_owner_record.lname

                val = {"iltId": ilt_record.id,
                       "title": ilt_record.title,
                       "description": ilt_record.description,
                       "ownerId": ilt_owner_record.id,
                       "ownerName": owner_name,
                       "latestMeetingId": latestMeetingId,
                       "meetingStatus": status}
                ilt_list.append(val)
            return ilt_list
        else:
            return []

    def get_ilt_details(self, user_id: int, ilt_id: int, db: Session):
        if db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none() is None:
            raise CustomException(400,  "records Not found")
        ilt_record = db.query(MdlIlts).filter(
            MdlIlts.id == ilt_id).one_or_none()
        if ilt_record is None:
            raise CustomException(400,  "records Not found")

        members_id_list = [record.member_id for record in db.query(
            MdlIltMembers).filter(MdlIltMembers.ilt_id == ilt_id).all()]
        school_record = db.query(MdlSchools).filter(
            MdlSchools.id == ilt_record.school_id).one()
        owner_record = db.query(MdlUsers).filter(
            MdlUsers.id == ilt_record.owner_id).one()
        member_info = []
        for uid in members_id_list:
            user_record = db.query(MdlUsers).filter(
                MdlUsers.id == uid).one()
            member_info.append({"userId": user_record.id,
                                "firstName": user_record.fname,
                                "lastName": user_record.lname,
                                "emailId": user_record.email})
        latestMeetingId = 0
        status = 0
        return {
            "iltId": ilt_record.id,
            "owner": {
                "userId": owner_record.id,
                "firstName": owner_record.fname,
                "lastName": owner_record.lname,
                "emailId": owner_record.email
            },
            "title": ilt_record.title,
            "description": ilt_record.description,
            "school": {
                "schoolId": school_record.id,
                "schoolName": school_record.name,
                "schoolDistrict": school_record.district
            },
            "latestMeetingId": latestMeetingId,
            "status": status,
            "members": member_info

        }

    def is_user_exist(self, user_id, db):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        if user is not None:
            return True
        else:
            return False

    def create_schools(self, name, location, district, db: Session):
        db_school = MdlSchools(name=name, location=location, district=district)
        db.add(db_school)
        db.commit()
        db.refresh(db_school)
        return {

            "statusCode": 200,
            "userMessage": "school has created successfully."
        }

    def create_ilts(self, owner_id, title, description, school_id, user_id, member_id_list, db: Session):
        # validating
        owner_re = db.query(MdlUsers).filter(
            MdlUsers.id == owner_id).one_or_none()
        if owner_re is None:
            raise CustomException(404,  "User not found")
        logged_user_re = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if logged_user_re is None:
            raise CustomException(404,  "user not found")
        school_re = db.query(MdlSchools).filter(
            MdlSchools.id == school_id).one_or_none()
        if school_re is None:
            raise CustomException(404,  "school not found")
        if bool(title and description) != True:
            raise CustomException(400,  "please enter title/description")
        title = title.strip()
        if title:
            #check if title is unique
            title1 = title.lower()
            ilt_record= (db.query(MdlIlts)
                .filter(and_(MdlIlts.school_id==school_id , func.lower(MdlIlts.title)==title1))
                .all())
            if ilt_record:
                raise CustomException(400,  "This Ilt already exists in the school, Please change the Ilt title")
        # verify all member id
        valid_member_id_list = []
        if len(member_id_list) > 0:
            member_id_list = list(set(member_id_list))
            try:
                valid_member_id_list = [db.query(MdlUsers).filter(
                    MdlUsers.id == m_id).first().id for m_id in member_id_list]
            except Exception as e:
                raise CustomException(
                    500,  f"please enter existing member id only. Error: {str(e)}")

        db_ilt = MdlIlts(owner_id=owner_id, created_by=user_id,
                         title=title, description=description, school_id=school_id)
        db.add(db_ilt)
        db.commit()
        db.refresh(db_ilt)
        # mapping all user's id with ilt in the map table also check uid existance
        if owner_id in valid_member_id_list:
            valid_member_id_list.remove(owner_id)
        valid_member_id_list.insert(0,owner_id) 
        
        for m_id in valid_member_id_list:
            # flag = self.is_user_exist(user_id = m_id, db=db)
            db_ilt_member = MdlIltMembers(ilt_id=db_ilt.id, member_id=m_id)
            db.add(db_ilt_member)
            db.commit()
            db.refresh(db_ilt_member)
        return {

            "statusCode": 200,
            "userMessage": "ilt has created successfully and added all members successfully"
        }

    def update_ilt(self, ilt_data: Ilt, user_id, ilt_id: int, db: Session):
        loging_user_record = db.query(MdlUsers).filter(
            MdlUsers.id == user_id).one_or_none()
        if loging_user_record is None or loging_user_record.role_id == 1:
            raise CustomException(
                404,  "this User can not perform the operation")
        if ilt_data.schoolId != 0:
            if db.query(MdlSchools).filter(MdlSchools.id == ilt_data.schoolId).one_or_none() is None:
                raise CustomException(400,  "school did not found")

        db_ilt = db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none()
        if db_ilt is None:
            raise CustomException(404,  "ilt did not found")
        if (db_ilt.owner_id != user_id) and (loging_user_record.role_id != 3):
            raise CustomException(404,  "this user can not modify the ilt")

        common_msg = ""
        # need to add members, change owner_id functionality
        if ilt_data.title:
            db_ilt.title = ilt_data.title
        if ilt_data.description:
            db_ilt.description = ilt_data.description
        if ilt_data.schoolId:
            db_ilt.school_id = ilt_data.schoolId
        if ilt_data.ownerId:
            common_msg = "unable to update ownerId for now!"
            # update tables - ilt, iltMember, upcoming_meetings_responce, for all rocks, and all user_maping
            pass
        db_ilt.updated_at = datetime.now()
        db_ilt.update_by = user_id
        db.commit()
        db.refresh(db_ilt)

        if len(ilt_data.memberIds) >= 1 and ilt_data.memberIds[0] != 0:
            if 0 in ilt_data.memberIds:
                raise CustomException(
                    500,  f"unable to process your request: found 0 in member list")
            msg, count = ("", 0)
            ilt_query = db.query(MdlIltMembers)
            # check if user exist
            verified_member_ids = []
            for m_re in list(set(ilt_data.memberIds)):
                ilt_record = ilt_query.filter(MdlIltMembers.ilt_id == ilt_id,
                                              MdlIltMembers.member_id == m_re).one_or_none()
                if ilt_record is not None:
                    count += 1
                else:
                    verified_member_ids.append(m_re)
                    db_ilt_member = MdlIltMembers(
                        ilt_id=ilt_id, member_id=m_re)  # adding to ilt_user_map
                    db.add(db_ilt_member)
                    db.commit()
                    db.refresh(db_ilt_member)

            current_date = datetime.now()
            upcoming_meeting_list = db.query(MdlMeetings)\
                .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)\
                .filter(MdlIltMeetings.ilt_id == ilt_id)\
                .filter(MdlMeetings.schedule_start_at > current_date)\
                .all()
            upcoming_meetingId_list = [
                record.id for record in upcoming_meeting_list]
            # creating meetingResponce for new members
            flag, msg = IltMeetingResponceService().create_meeting_responses_empty_for_newMember_for_all_meetings(
                meeting_ids=upcoming_meetingId_list, member_list=verified_member_ids, db=db
            )

            if flag != True:
                raise CustomException(
                    404,  f"unable to process your request, {msg}")
            else:
                emsg = "ilt has Updated successfully with all new members."
                if count > 0:
                    emsg = f"ilt has Updated successfully with all new member whereas {count} member already exist in the ilt"
                return {

                    "statusCode": 200,
                    "userMessage": emsg+common_msg
                }

        return {

            "statusCode": 200,
            "userMessage": f"ilt has Updated successfully. {common_msg}"
        }

    def get_list_of_ilt_rocks(self, iltId: int, db: Session):
        ilt_record = db.query(MdlIlts).filter(
            MdlIlts.id == iltId).one_or_none()
        if ilt_record is None:
            raise CustomException(400,  "ilt does not exist")

        # re = db.query(MdlIlt_rocks).filter(MdlIlt_rocks.ilt_rock_id == iltId).all()
        rock_records = (
            db.query(MdlRocks)
            # .join(MdlIlt_rocks, MdlRocks.ilt_id == MdlIlt_rocks.ilt_id)
            .filter(MdlRocks.ilt_id == iltId)
            .all()
        )

        ilt_rock_details = [{
            "id":  ilt_rock_detail.id,
            "name": ilt_rock_detail.name,
            "description": ilt_rock_detail.description,
            "ownerId": ilt_rock_detail.owner_id if ilt_rock_detail.owner_id else "OwnerId not assigned"
        } for ilt_rock_detail in rock_records]

        return ilt_rock_details
