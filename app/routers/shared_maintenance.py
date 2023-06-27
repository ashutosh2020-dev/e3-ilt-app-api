from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.shared_service import SharedService

router = APIRouter()
shared_service = SharedService()

@router.get("/api/v1/shared/schools")
def fn_read_list_of_schools( db: Session = Depends(get_db)):
    return shared_service.get_list_of_schools( db =db)

# @router.get("/api/v1/shared/rock")
# def fn_read_list_of_rocks( db: Session = Depends(get_db)):
#     return shared_service.get_list_of_rocks( db =db)

@router.get("/api/v1/shared/roles")
def fn_get_role_details( db: Session = Depends(get_db)):
    return shared_service.get_role_details( db =db)

@router.get("/api/v1/shared/priorities")
def  fn_get_priority_details( db:Session= Depends(get_db)):
    return shared_service.get_priority_details( db=db)

@router.get("/api/v1/shared/lookup")
def fn_get_lookup( db:Session=Depends(get_db)):
    return shared_service.get_lookup_details( db=db)