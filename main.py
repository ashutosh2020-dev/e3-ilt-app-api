from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config.app_settings import settings
from app.config.database import engine, SessionLocal, Base
from app.routers import user_maintenance, dashboard_maintenance, ilt_maintenance, ilt_meeting_maintenance,\
                ilt_meeting_response_maintenance, shared_maintenance, other_maintenance, login_maintenance
import uvicorn
from app.exceptions.customException import CustomException
from fastapi.responses import JSONResponse


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
        "name": "User Dashboard",
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
     {
        "name": "Shared Maintenance",
        "description": "Contains School names,Rocks,roles",
        
    },
    {
        "name": "Others",
        "description": "Contains School names,Rocks,roles",
        
    }
]

app = FastAPI(
                title=settings.app_name,
                version=settings.app_version,
                description=settings.app_description
                )
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.code,
        content={"statusCode": exc.code, "userMessage": exc.message}
    )

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"statusCode": 500, "userMessage": str(exc)}
    )

@app.exception_handler(RequestValidationError)
async def Request_Validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"statusCode": 422, "userMessage": exc.errors()}
    )

Base.metadata.create_all(bind=engine)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
app.include_router(ilt_maintenance.router, tags=["ILT Maintenance"])
app.include_router(dashboard_maintenance.router, tags=["User Dashboard"])
app.include_router(login_maintenance.router, tags=["User Login"])
app.include_router(user_maintenance.router, tags=["User Maintenance"])
app.include_router(ilt_meeting_maintenance.router, tags=["Ilt Meetings Maintenance"])
app.include_router(ilt_meeting_response_maintenance.router, tags=["ILT Meeting Response Maintenance"])
app.include_router(shared_maintenance.router, tags=["Shared Maintenance"])
app.include_router(other_maintenance.router, tags=["Others"])

@app.get("/")
def home():
    return {"Request":"Success"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=True, workers=4)