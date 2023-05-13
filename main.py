# from typing import Union
# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()


# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}

# class experimental(BaseModel):
#     title : str
#     body : str
#     # others : Optional[bool]


# @app.post('/lets_see')
# async def create_someting(request_name : experimental):
#     return {f"the project title is - {request_name.title} and body is {request_name.body}"}


# @app.get("/blogs")
# async def read_root(limit):
#     return {"Data": f"{limit} numbers of blogs are"}

# @app.get("/{id}/comments")

# async def comment(id : int):
#     return {"the id is ":id}


from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# SQLALCHEMY_DATABASE_URL = "sqlite:///ILT_Project2.db"
engine = create_engine('sqlite:///C:\\Users\\91740\\Desktop\\SortingHat\\ILT_Project2.db', echo=False)
print("engine :",engine)
#C:\Users\91740\Desktop\SortingHat\ILT_Project2.db
#engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
print("base created :",Base)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "user_csv"
    id = Column('user_id',Integer,primary_key=True)                      #Column(Integer, primary_key=True, index=True)
    user_id  = Column('email_id',String)                                 #Column(String, unique=True, index=True)
    password = Column('password',String)

    def verify_password(self, password):
        return self.password == password

    # def verify_password(self, password):
    #     return pwd_context.verify(password, self.hashed_password)

print('user details :',User)

db = SessionLocal()

try:
    # Retrieve the first 5 records from the User table
    users = db.query(User).limit(5).all()
    for user in users:
        print(user.id, user.user_id,user.password)
except Exception as e:
    print("Error retrieving data from the database:", e)
finally:
    # Close the session
    db.close()

# Base.metadata.create_all(bind=engine)

security = HTTPBasic()

def get_db():
    with SessionLocal() as db:
        try:
            yield db
        finally:
            db.close()

@app.post("/api/v1/login")
def login(credentials: HTTPBasicCredentials, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == credentials.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.verify_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # if not pwd_context.verify(credentials.password, user.hashed_password):
    #     raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Logged in successfully"}