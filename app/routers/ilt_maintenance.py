from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_services import IltService


router = APIRouter()
IltService = IltService()

@router.get("/api/v1/ilts/")
def read_ilts_for_user(user_id: int, db: Session = Depends(get_db)):
    return IltService.get_Ilts_list(user_id = user_id, db = db)

@router.post("/api/v1/ilts/")
async def create_ilt(user_id:int, title: str, description: str, 
                     school_id: int, member_id: list ,db: Session = Depends(get_db)):
    return IltService.create_ilts(owner_id = user_id, title = title, description = description, school_id = school_id,
                            member_id_list = member_id, db = db)

@router.get("/api/v1/ilts/{id}")
def read_ilts_for_user(id: int, db: Session = Depends(get_db)):
    return IltService.get_ilt_details(ilt_id = id, db = db)


# @router.post("/api/v1/ilts/{id}")
# def update_ilt(ilt_id:int, user_id:int, title: str, description: str, \
#                      school_id: int, member_id: list ,db: Session = Depends(get_db)):
#     return IltService.update_ilt()    
# @router.get("/api/v1/ilts/{id}") # Get List of ilts for a given user.
# @router.post("/api/v1/ilts/{id}") # Create new ILT for a given user.