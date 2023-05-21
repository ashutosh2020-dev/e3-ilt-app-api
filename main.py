from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.config.app_settings import settings
from app.config.database import engine, SessionLocal, Base
from app.routers import user_maintenance, ilt_maintenance, ilt_meeting_maintenance, ilt_meeting_response_maintenance
import uvicorn

tags_metadata = [
    {
        "name": "ILT Maintenance",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "User Login",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "User Maintenance",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "write external details here",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
    {
        "name": "Ilt Meetings Maintenance",
        "description": "Manage items. So _fancy_ they have their own docs.",
        
    },
    {
        "name": "ILT Meeting Response Maintenance",
        "description": "Manage items. So _fancy_ they have their own docs.",
        
    },
]

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description
    )
Base.metadata.create_all(bind=engine)

app.include_router(ilt_maintenance.router, tags=["ILT Maintenance"])
app.include_router(user_maintenance.router, tags=["User Maintenance"])
app.include_router(ilt_meeting_maintenance.router, tags=["Ilt Meetings Maintenance"])
app.include_router(ilt_meeting_response_maintenance.router, tags=["ILT Meeting Response Maintenance"])


if __name__ == "__main__":
    # uvicorn.run("main:app", host="127.0.0.1", port=settings.app_port, reload=True)
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=True)