from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.shared_service import SharedService

router = APIRouter()
shared_service = SharedService()

@router.get("/api/v1/shared/schools")
def fn_read_list_of_schools(user_id: int, db: Session = Depends(get_db)):
    return shared_service.get_list_of_schools(user_id, db =db)

@router.get("/api/v1/shared/rock")
def fn_read_list_of_rocks(user_id: int, db: Session = Depends(get_db)):
    return shared_service.get_list_of_rocks(user_id, db =db)

@router.get("/api/v1/shared/roles")
def fn_get_role_details(user_id: int, db: Session = Depends(get_db)):
    return shared_service.get_role_details(user_id, db =db)

@router.get("/api/v1/shared/priorities")
def  fn_get_priority_details(UserId, db:Session= Depends(get_db)):
    return shared_service.get_priority_details(UserId, db=db)

@router.get("/api/v1/shared/lookup")
def fn_get_lookup(user_id, db:Session=Depends(get_db)):
    return shared_service.get_lookup_details(user_id = user_id, db=db)