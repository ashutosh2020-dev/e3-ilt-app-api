from fastapi import APIRouter, Depends
# from fastapi.responses import FileResponse
from starlette.responses import FileResponse
import os
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.other_services import Create_otherService
from app.schemas.other_schemas import User, school, Role, priority, district

file_name = "ilt_db.db"
file_path = "ilt_db.db"

router = APIRouter()
create_api_service = Create_otherService()
        
@router.post("/api/v1/other/root_user/")
def fn_create_admin_user(user:User,
                   db: Session = Depends(get_db)):
    return create_api_service.create_root_user(fname=user.firstName, 
                                                lname=user.lastName,
                                                email=user.emailId,
                                                number=user.phoneNumber, 
                                                password=user.password, 
                                                is_active=user.active,
                                                role_id=user.roleId,
                                                districts=user.districts,
                                                db=db)


@router.post("/api/v1/others/schools/")
def fn_create_school_record( school:school,db:Session=Depends(get_db)):
    return create_api_service.create_schools(name=school.name, 
                                             location=school.location, 
                                             districtId=school.districtId, 
                                             db=db)

@router.post("/api/v1/others/roles/")
def create_user_roles(role:Role, db:Session=Depends(get_db)):
    return create_api_service.create_roles(role_name=role.role_name, roleDescription=role.roleDescription, db=db)

@router.post("/api/v1/others/priority/")
def create_user_priority(priority:priority, db:Session=Depends(get_db)):
    return create_api_service.create_priority( name=priority.name, description=priority.description, db=db)

@router.post("/api/v1/others/district/")
def create_district(district:district, db:Session=Depends(get_db)):
    return create_api_service.create_district( name=district.name, db=db)

@router.get("/api/v1/others/download-db/")
def download_Ilt_db():
    return FileResponse(file_path, filename=file_name)
