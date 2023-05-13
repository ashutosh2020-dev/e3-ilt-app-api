from fastapi import FastAPI, HTTPException,Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\Users\\91740\\Desktop\\SortingHat\\ILT_Project2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "user_csv"
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email_id = Column(String)
    phone_number = Column(String)
    password = Column(String)
    is_active = Column(Integer)
    role_id = Column(Integer)
    parent_user_id = Column(Integer)

class ILTMember(Base):
    __tablename__ = "ilt_members_csv"
    id = Column(Integer, primary_key=True)
    ilt_id = Column(Integer, ForeignKey('ilts_csv.ilt_id'))
    member_id = Column(Integer, ForeignKey('user_csv.user_id'))
    user = relationship(User, foreign_keys=[member_id])

class ILT(Base):
    __tablename__ = "ilts_csv"
    ilt_id = Column(Integer, primary_key=True)
    ilt_owner = Column(Integer)
    ilt_title = Column(String)
    ilt_description = Column(String)
    members = relationship(ILTMember)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()    

@app.get("/api/v1/ilts")
def get_user_ilts(user_id: int, db: Session = Depends(get_db)):
    ilts = db.query(ILT).join(ILT.members).filter(ILTMember.member_id == user_id).all()
    if not ilts:
        raise HTTPException(status_code=404, detail="No ILTs found for the user")
    return [
        {
            "ilt_id": ilt.ilt_id,
            "ilt_owner": ilt.ilt_owner,
            "title": ilt.ilt_title,
            "description": ilt.ilt_description
        }
        for ilt in ilts
    ]