from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.ilt_services import IltService

router = APIRouter()
Dashboard_Service = DashboardService()

@router.post("/api/dashboard")
async def create_ilt(user_id:int, ilt_id :int, db: Session = Depends(get_db)):
    return Dashboard_Service.get_ilt_dashboard_info(user_id=user_id, ilt_id=ilt_id, db=db)

