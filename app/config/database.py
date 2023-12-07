from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

server_url = "UAT"  # "PROD"
DATABASE_URLS_DICT = {
                        "PROD":"mysql://sortinghatadmin:Sortinghat#Middle123@rds-middle-ilt-app.c61momvubcsz.us-east-1.rds.amazonaws.com:3306/dbiltapp",
                        "UAT": "mysql://sortinghatadmin:Sortinghat#Middle123@rds-middle-ilt-app.c61momvubcsz.us-east-1.rds.amazonaws.com:3306/dbiltappuat",
                        "sqllite": "sqlite:///ilt_db.db"
                    }
DATABASE_URL = DATABASE_URLS_DICT.get(server_url) 
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()