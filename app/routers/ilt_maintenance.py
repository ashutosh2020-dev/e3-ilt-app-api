from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_services import IltService
from typing import Annotated, Union
from app.schemas.ilt_schemas import Ilt, Createilt

router = APIRouter()
IltService = IltService()

@router.get("/api/v1/ilts/")
def read_ilts_for_user(UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltService.get_Ilts_list(user_id = UserId, db = db)

@router.post("/api/v1/ilts/")
async def create_ilt(Createilt:Createilt, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltService.create_ilts(owner_id = Createilt.owner_id, 
                                  user_id=UserId, 
                                  title = Createilt.title, 
                                  description = Createilt.description, 
                                  school_id = Createilt.schoolId,
                                  member_id_list = Createilt.memberIds, 
                                  db = db)

@router.get("/api/v1/ilts/{id}")
def read_ilts_description(id: int, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return IltService.get_ilt_details(user_id= UserId, ilt_id = id, db = db)

 
@router.post("/api/v1/ilts/{id}")
def update_ilt(ilt_data:Ilt, id:int, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return  IltService.update_ilt(ilt_data=ilt_data, user_id =UserId, ilt_id=id, db=db)
