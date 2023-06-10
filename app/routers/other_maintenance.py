from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.other_services import Create_otherService

router = APIRouter()
create_api_service = Create_otherService()

        
@router.post("/api/v1/other/root_user/")
def fn_create_admin_user(fname: str, lname: str, email: str, number: str, \
                   password: str, is_active: bool, role_id: int, db: Session = Depends(get_db)):
    return create_api_service.create_root_user(fname=fname, lname=lname, email=email, number=number, 
                                         password=password, is_active=is_active, role_id=role_id, db=db)

@router.post("/api/v1/others/schools/")
def fn_create_school_record(name:str, location:str, district:str, db:Session=Depends(get_db)):
    return create_api_service.create_schools(name=name, location=location, district=district, db=db)

@router.post("/api/v1/others/roles/")
def create_user_roles(role_name:str, roleDescription:str, db:Session=Depends(get_db)):
    return create_api_service.create_roles(role_name=role_name, roleDescription=roleDescription, db=db)

@router.post("/api/v1/others/priority/")
def create_user_priority(role_id:int, name:str, description:str, db:Session=Depends(get_db)):
    return create_api_service.create_priority(role_id = role_id, name=name, description=description, db=db)