from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter()
Dashboard_Service = DashboardService()

@router.get("/api/dashboard/ilt/{iltId}")
async def Show_Ilt_Dashboard( iltId :int, UserId: int=Header(convert_underscores=False), db: Session = Depends(get_db)):
    return Dashboard_Service.get_ilt_Meetings_dashboard_info(user_id=UserId, ilt_id=iltId, db=db)