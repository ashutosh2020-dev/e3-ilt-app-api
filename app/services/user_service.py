from sqlalchemy.orm import Session
from app.models import MdlUsers

class UserService:
    def get_user(self, user_id: int, db: Session):
        return db.query(MdlUsers).filter(MdlUsers.id == user_id).first()

    def create_user(self, UserId, fname, lname, email, number, password, is_active, role_id, db: Session):
        db_user = MdlUsers(fname=fname, lname=lname, email=email, number=number, \
                           password=password, is_active=is_active, role_id=role_id, parent_user_id= UserId)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return True

    def update_user(self, user_id: int, fname, lname, email, number, password, is_active, role_id, db: Session):
        db_user = db.query(MdlUsers).filter(MdlUsers.id == user_id).first()
        if db_user:
            db_user.fname = fname
            db_user.lname = lname
            db_user.email = email
            db_user.number = number
            db_user.password = password
            db_user.is_active = is_active
            db_user.role_id = role_id
            db.commit()
            db.refresh(db_user)
            return True
        else:
            return False

    # def delete_user(self, user_id)
