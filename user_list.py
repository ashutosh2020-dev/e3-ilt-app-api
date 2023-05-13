from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\Users\\91740\\Desktop\\SortingHat\\ILT_Project2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# class User(Base):
#     __tablename__ = "user_csv"
#     id = Column('user_id',Integer,primary_key=True)                      #Column(Integer, primary_key=True, index=True)
#     user_id  = Column('email_id',String)                                 #Column(String, unique=True, index=True)
#     password = Column('password',String)
#     first_name = Column('first_name',String)
#     last_name = Column('last_name',String)

db = SessionLocal()

Base.metadata.create_all(bind=engine)

def get_db():
    with SessionLocal() as db:
        try:
            yield db
        finally:
            db.close()

@app.get("/api/v1/users")
def get_users(db: Session = Depends(get_db)):
    users = db.execute(text("SELECT user_id,first_name,last_name,email_id,phone_number,password,is_active,role_id FROM user_csv")).all()
    users = [dict(zip(("user_id","first_name","last_name","email_id","phone_number",'password','is_active','role_id'), user)) for user in users]
    return {"users": users}


    # users = db.query(User.first_name, User.last_name).all()
    # users = [dict(zip(('first_name', 'last_name'), user)) for user in users]
    # return {"users": users}
