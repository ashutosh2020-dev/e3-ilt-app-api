from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\Users\\91740\\Desktop\\SortingHat\\ILT_Project2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "user_csv"
    id = Column('user_id', Integer, primary_key=True)
    user_id = Column('email_id', String)
    password = Column('password', String)
    first_name = Column('first_name', String)
    last_name = Column('last_name', String)
    phone_number = Column('phone_number', String)
    active = Column('is_active', Integer)
    role_id = Column('role_id', Integer)


Base.metadata.create_all(bind=engine)

security = HTTPBasic()

def get_db():
    with SessionLocal() as db:
        try:
            yield db
        finally:
            db.close()

@app.post("/api/v1/users/{id}")
def update_user(id: int, password: str, first_name: str, last_name: str,
                email_id: str, phone_number: str, active: bool, role_id: int,
                db: Session = Depends(get_db)):

    user = db.query(User).filter_by(id=id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if first_name:
        user.first_name = first_name

    if last_name:
        user.last_name = last_name

    if email_id:
        user.user_id = email_id

    if phone_number:
        user.phone_number = phone_number

    if active is not None:
        user.active = active

    if role_id:
        user.role_id = role_id

    db.commit()

    return {"message": "User updated successfully."}


@app.get("/api/v1/users")
def get_users(db: Session = Depends(get_db)):
    users = db.execute(text("SELECT user_id,first_name,last_name,email_id,phone_number,password,is_active,role_id FROM user_csv")).all()
    users = [dict(zip(("user_id","first_name","last_name","email_id","phone_number",'password','is_active','role_id'), user)) for user in users]
    return {"users": users}