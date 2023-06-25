from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, join
from app.models import MdlIlts, MdlIltMembers, MdlUsers, MdlSchools, MdlMeetings, MdlIltMeetings
from app.schemas.ilt_schemas import Ilt
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
from app.exceptions.customException import CustomException
# from pytz import utc

def calculate_meeting_status(schedule_start_at, start_at, end_at):
    current_datetime = datetime.now(timezone.utc)
    if current_datetime < schedule_start_at:
        return 0  # notStarted
    elif current_datetime >= start_at and current_datetime <= end_at:
        return 1  # inProgress
    else:
        return 2  # completed

class IltService:
    def get_Ilts_list(self, user_id: int, db: Session):
        ilt_list = []
        list_ilts = [record.ilt_id for record in db.query(MdlIltMembers).filter(MdlIltMembers.member_id == user_id).all()]
        print(list_ilts)
        if list_ilts:
            for x in list_ilts:
                ilt_record = db.query(MdlIlts).filter(MdlIlts.id == x).first()
                ilt_owner_record = db.query(MdlUsers).filter(MdlUsers.id == ilt_record.owner_id).first()
                owner_name = ilt_owner_record.fname+" "+ilt_owner_record.lname
                # find latest meeting
                # current_datetime = datetime.now(timezone.utc)
                # meeting_ids = [re.ilt_meeting_id for re in db.query(MdlIltMeetings).filter(MdlIltMeetings.ilt_id==x).all()]
                # meeting_record = (db.query(MdlMeetings)
                #                     .filter( MdlMeetings.schedule_start_at < current_datetime)
                #                     .order_by(desc(MdlMeetings.schedule_start_at))
                #                     .first())
                meeting_record = (
                                db.query(MdlMeetings)
                                .join(MdlIltMeetings, MdlMeetings.id == MdlIltMeetings.ilt_meeting_id)
                                .order_by(desc(MdlMeetings.schedule_start_at))
                                .first()
                            )

                if meeting_record:
                    latestMeetingId = meeting_record.id
                    start_meeting_time =  meeting_record.schedule_start_at.replace(tzinfo=timezone.utc) #datetime.strptime(ilt_meeting_start_time, '%Y-%m-%d %H:%M:%S.%f')
                    end_meeting_time = meeting_record.end_at.replace(tzinfo=timezone.utc)
                    status = calculate_meeting_status(start_meeting_time, start_meeting_time, end_meeting_time)
                else:
                    latestMeetingId = 0
                    status = 0
                val = {"iltId":ilt_record.id, 
                       "tittle":ilt_record.title, 
                       "description": ilt_record.description, 
                       "ownerName":owner_name,
                       "latestMeetingId":latestMeetingId,
                       "meetingStatus": status}
                ilt_list.append(val)
            return ilt_list
        raise CustomException(400,  "records Not found")
    def get_ilt_details(self, user_id:int, ilt_id:int, db:Session):
        try:

            if db.query(MdlUsers).filter(MdlUsers.id==user_id).one_or_none() is None:
                raise CustomException(404,  "userId did not found")
            ilt_record = db.query(MdlIlts).filter(MdlIlts.id==ilt_id).one_or_none()
            if ilt_record is None:
                raise CustomException(400,  "records Not found")
            
            members_id_list = [record.member_id for record in db.query(MdlIltMembers).filter(MdlIltMembers.ilt_id==ilt_id).all()]
            school_record = db.query(MdlSchools).filter(MdlSchools.id==ilt_record.school_id).one()
            owner_record = db.query(MdlUsers).filter(MdlUsers.id==ilt_record.owner_id).one()
            member_info = []
            for uid in members_id_list:
                user_record = db.query(MdlUsers).filter(MdlUsers.id==uid).one()
                member_info.append({"userId":user_record.id,
                                    "firstName":user_record.fname, 
                                    "lastName":user_record.lname})
            return {
                    "iltId": ilt_record.id,
                    "owner": {
                        "userId": owner_record.id,
                        "firstName": owner_record.fname,
                        "lastName": owner_record.lname
                    },
                    "title": ilt_record.title,
                    "description": ilt_record.description,
                    "school": {
                        "schoolId": school_record.id,
                        "schoolName": school_record.name,
                        "schoolDistrict": school_record.district
                    },
                    "members": member_info
                    }
        except Exception as e:
            return None
    
    def is_user_exist(self, user_id, db):
        user = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
        if user is not None:
            return True
        else:
            return False
        
    def create_schools(self, name, location, district, db:Session):
        db_school = MdlSchools(name=name, location=location, district=district)
        db.add(db_school)
        db.commit()
        db.refresh(db_school) 
        return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "school has created successfully."
                }
    def create_ilts(self, owner_id, title, description, school_id, user_id, member_id_list, db: Session):
        try:
            # validate school id existance
            owner_re = db.query(MdlUsers).filter(MdlUsers.id == owner_id).one_or_none()
            if owner_re is None:
                raise CustomException(404,  "User not found")
            logged_user_re = db.query(MdlUsers).filter(MdlUsers.id == user_id).one_or_none()
            if logged_user_re is None:
                raise CustomException(404,  "user not found")
            school_re = db.query(MdlSchools).filter(MdlSchools.id == school_id).one_or_none()
            if school_re is None:
                raise CustomException(404,  "school not found")
            # verify all member id
            if len(member_id_list)==0:
                raise CustomException(500,  "please member list.")
            member_id_list = list(set(member_id_list))
            try:
                valid_member_id_list = [db.query(MdlUsers).filter(MdlUsers.id == m_id).first().id for m_id in member_id_list]
            except Exception as e:
                raise CustomException(500,  f"please enter existing member id only. Error: {str(e)}")
            
            db_ilt = MdlIlts(owner_id = owner_id,created_by=user_id, title= title, description= description, school_id= school_id)
            db.add(db_ilt)
            db.commit()
            db.refresh(db_ilt)
            
            # mapping all user's id with ilt in the map table also check uid existance
            for m_id in valid_member_id_list:
                # flag = self.is_user_exist(user_id = m_id, db=db)
                db_ilt_member = MdlIltMembers(ilt_id = db_ilt.id, member_id = m_id)
                db.add(db_ilt_member)
                db.commit()
                db.refresh(db_ilt_member)
            return {
                "confirmMessageID": "string",
                "statusCode": 200,
                "userMessage": "ilt has created successfully and added all members successfully"
                }
        except SQLAlchemyError as e:
            # db.rollback()
            raise CustomException(500,  f"Failed to store data in the database. Error: {str(e)}")
        except Exception as e:
            # db.rollback()
            raise CustomException(500,  f"unable to process your request: {str(e)}")

    
    def update_ilt(self,ilt_data:Ilt,user_id, ilt_id, db: Session):
        try:
            if db.query(MdlUsers).filter(MdlUsers.id==user_id).one_or_none() is None:
                raise CustomException(404,  "User did not found")
            if ilt_data.schoolId != 0:
                if db.query(MdlSchools).filter(MdlSchools.id == ilt_data.schoolId).one_or_none() is None:
                    raise CustomException(400,  "school did not found")
            db_ilt = db.query(MdlIlts).filter(MdlIlts.id == ilt_id).one_or_none()
            if db_ilt is None:
                raise CustomException(404,  "ilt did not found")
            # need to add members, change owner_id functionality 
            if ilt_data.title:
                db_ilt.title = ilt_data.title
            if ilt_data.description:
                db_ilt.description = ilt_data.description
            if ilt_data.schoolId:    
                db_ilt.school_id = ilt_data.schoolId
            db.commit()
            db.refresh(db_ilt)
            return {
                    "confirmMessageID": "string",
                    "statusCode": 200,
                    "userMessage": "ilt has updated successfully"
                }
        except Exception as e:
            raise CustomException(500,  "unable to process your request")