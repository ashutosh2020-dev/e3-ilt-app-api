from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard_schemas import DashboardFilterParamaters 
router = APIRouter()
Dashboard_Service = DashboardService()

@router.get("/api/v1/dashboard/ilt/{iltId}")
async def Show_Ilt_Dashboard( iltId :int, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return Dashboard_Service.get_ilt_Meetings_dashboard_info(user_id=UserId, ilt_id=iltId, db=db)

@router.get("/api/v1/dashboard/ilt/{iltId}/meeting/{meetingId}")
async def Show_Ilt_Dashboard_wrt_meeting( iltId :int, meetingId:int, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return Dashboard_Service.get_ilt_Meeting_dashboard_info(user_id=UserId, ilt_id=iltId,meetingId=meetingId, db=db)

@router.get("/api/v1/dashboard/userId/{userId}/")
async def Show_Ilt_Dashboard_wrt_schools( userId: int, db: Session = Depends(get_db)):
    return Dashboard_Service.get_detailed_dashboard_info(user_id=userId, db=db)

@router.post("/api/v1/dashboard/userId/{userId}/")
async def Show_Ilt_Dashboard_wrt_schools_filterby_district( userId: int, FilterParamaters:DashboardFilterParamaters, db: Session = Depends(get_db)):
    return Dashboard_Service.get_detailed_dashboard_info(user_id=userId, FilterParamaters=FilterParamaters, db=db)