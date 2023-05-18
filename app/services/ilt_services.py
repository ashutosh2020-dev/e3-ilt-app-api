from sqlalchemy.orm import Session
from app.models import MdlIlts, MdlIltMembers, MdlUsers

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
                val = {"id":ilt_record.id, "title":ilt_record.title, "description": ilt_record.description, "owner":owner_name}
                ilt_list.append(val)
            return ilt_list
        return {
        "confirmMessageID": "string",
        "statusCode": 0,
        "userMessage": "records Not found"
        }

    def create_ilts(self, owner_id, title, description, school_id, member_id_list, db: Session):
        #validate owner id and school id existance
        user = db.query(MdlUsers).filter(MdlUsers.id == owner_id).first()
        if not user:
            return {
                "confirmMessageID": "string",
                "statusCode": 400,
                "userMessage": "User not found"
                }
        db_ilt = MdlIlts(owner_id = owner_id, title= title, description= description, school_id= school_id)
        db.add(db_ilt)
        db.commit()
        db.refresh(db_ilt)
        print(db_ilt.id)
        for m_id in member_id_list:
            db_ilt_member = MdlIltMembers(ilt_id = db_ilt.id, member_id = m_id)
            db.add(db_ilt_member)
            db.commit()
            db.refresh(db_ilt_member)
        return True

    # def update_ilt(self, ilt_id: int, fname, lname, email, number, password, is_active, role_id, db: Session):
    #     db_user = db.query(MdlIlts).filter(MdlIlts.id == ilt_id).first()
    #     if db_user: # fields -> owner_id, title, description, school_id
    #         db_user.fname = fname
    #         db_user.lname = lname
    #         db_user.email = email
    #         db_user.number = number
    #         db_user.password = password
    #         db_user.is_active = is_active
    #         db_user.role_id = role_id
    #         db.commit()
    #         db.refresh(db_user)
    #         return True
    #     else:
    #         return False

