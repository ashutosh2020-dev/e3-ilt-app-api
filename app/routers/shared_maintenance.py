from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.shared_service import SharedService

router = APIRouter()
shared_service = SharedService()

@router.get("/api/v1/shared/schools")
def fn_read_list_of_schools(UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return shared_service.get_list_of_schools(UserId, db =db)

@router.get("/api/v1/shared/rock")
def fn_read_list_of_rocks(UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return shared_service.get_list_of_rocks(UserId, db =db)

@router.get("/api/v1/shared/roles")
def fn_get_role_details(UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return shared_service.get_role_details(UserId, db =db)

@router.get("/api/v1/shared/priorities")
def  fn_get_priority_details(UserId: int=Header(convert_underscores=False), db:Session= Depends(get_db)):
    return shared_service.get_priority_details(UserId, db=db)

@router.get("/api/v1/shared/lookup")
def fn_get_lookup(UserId: int=Header(convert_underscores=False), db:Session=Depends(get_db)):
    return shared_service.get_lookup_details(user_id = UserId, db=db)