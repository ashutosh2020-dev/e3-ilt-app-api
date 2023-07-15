from sqlalchemy.orm import Session
from app.models import MdlSchools
from app.models import MdlRocks, MdlRoles, MdlPriorities, MdlDistrict
from app.exceptions.customException import CustomException

class SharedService:
    def get_list_of_schools(self,  db: Session):

        ilt_school_detail = [{
                                "schoolId" :  ilt_school_detail.id,
                                "schoolName" : ilt_school_detail.name,
                                "schoolDistrict" : ilt_school_detail.district
                                } for ilt_school_detail in db.query(MdlSchools).all()]

        return ilt_school_detail
        
        
        

    def get_list_of_rocks(self, db: Session):
        try:
            
            ilt_rock_details = [{
                                    "rockId" :  record.id,
                                    "description" : record.name,
                                 } for record in db.query(MdlRocks).all()]

            return ilt_rock_details
        
        except Exception as e:
            raise CustomException(500, f"unable to process your requests {e}")

    def get_list_of_districts(self, db:Session):
        ilt_district_detail = [{
                                "distictId" :  ilt_school_detail.id,
                                "distictName" : ilt_school_detail.name
                                } for ilt_school_detail in db.query(MdlDistrict).all()]

        return ilt_district_detail

    def get_role_details(self,db: Session):
        try:
            roles = [{
                            "roleId": record.id,
                            "roleName": record.name,
                            "roleDescription": record.description
                        } for record in db.query(MdlRoles).all()]

            return roles
        
        except Exception as e:
            raise CustomException(500, f"unable to process your requests {e}")
        
    def get_priority_details(self, db:Session):
        try:
            priority = [{
                            "priorityId": record.id,
                            "name": record.name,
                            "description": record.description
                        } for record in db.query(MdlPriorities).all()]

            return priority
        
        except Exception as e:
            raise CustomException(500, f"unable to process your requests {e}")
    def get_lookup_details(self, db:Session):
        try:

            school_details = [{
                                    "schoolId" :  record.id,
                                    "schoolName" : record.name,
                                    "schoolDistrict" : record.district
                                 } for record in db.query(MdlSchools).all()]
            rock_details = [{
                                    "rockId" :  record.id,
                                    "description" : record.name,
                                 } for record in db.query(MdlRocks).all()]
            roles = [{
                            "roleId": record.id,
                            "roleName": record.name,
                            "roleDescription": record.description
                        } for record in db.query(MdlRoles).all()]
            
            priorities = [{
                            "priorityId": record.id,
                            "name": record.name,
                            "description": record.description
                        } for record in db.query(MdlPriorities).all()]

            return  {"roles":roles,
                "priorities":priorities,
                "schools":school_details,
                "rocks": rock_details}
        
            # ilts_record = db.query(MdlIltMembers).filter(MdlIltMembers.member_id == user_id).all()
            # school_id_list = []
            # for record in ilts_record:
            #     ilt_school_id = db.query(MdlIlts).filter(MdlIlts.id == record.ilt_id).one().school_id
            #     school_id_list.append(ilt_school_id)

            # school_id_list = list(set(school_id_list))

            # ilt_schools_list = []

            # for school in school_id_list:
            #     ilt_school_detail = db.query(MdlSchools).filter(MdlSchools.id == school).one()
            #     ilt_schools_list.append({
            #         "schoolId" :  ilt_school_detail.id,
            #         "schoolName" : ilt_school_detail.name,
            #         "schoolDistrict" : ilt_school_detail.district})

            
            # meeting_record = db.query(MdlIltMeetingResponses).filter(MdlIltMeetingResponses.meeting_user_id == user_id).all()
            # meeting_response_id_list = []

            # for record in meeting_record:
            #     meeting_response_id_list.append(record.meeting_response_id)

            # rock_id_list = []    

            # for response_id in meeting_response_id_list:
            #     rocks = db.query(MdlMeeting_rocks).filter(MdlMeeting_rocks.ilt_meeting_response_id == response_id).all()
            #     rock_ids = [rock.rock_id for rock in rocks]
            #     rock_id_list.extend(rock_ids)

            # rock_id_list = list(set(rock_id_list))

            # rock_details_list = []

            # for rock_id in rock_id_list:
            #     rock_details = db.query(MdlRocks).filter(MdlRocks.id == rock_id).one()
            #     rock_details_list.append({
            #         "rockId" : rock_details.id,
            #         "description" : rock_details.description  
            #     })

            # return [{"roles":rock_details_list, "schools":ilt_schools_list}]
        except Exception as e:
            raise CustomException(500,  f"Internal Error, unable to process your request {e}")