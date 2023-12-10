from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sqlalchemy.orm import Session
from app.config.app_settings import settings
from app.config.database import engine, SessionLocal, Base
from app.routers import user_maintenance, dashboard_maintenance, ilt_maintenance, ilt_meeting_maintenance,\
                ilt_meeting_response_maintenance, shared_maintenance, other_maintenance, login_maintenance
import uvicorn
from app.exceptions.customException import CustomException
from fastapi.responses import JSONResponse
import os
import ssl
sslSettings = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
keyfile_path = os.path.abspath(
    os.path.join(os.getcwd(), 'certs', 'private.key'))
certfile_path = os.path.abspath(os.path.join(
    os.getcwd(), 'certs', 'certificate.crt'))
cafile_path = os.path.abspath(os.path.join(
    os.getcwd(), 'certs', 'ca_bundle.crt'))

# print('\nCERTFILE PATH\n', certfile_path)
# print('\nKEYFILE PATH\n', keyfile_path)s
# print('\nCAFILE PATH\n', cafile_path)
sslSettings.load_verify_locations(cafile=cafile_path)
sslSettings.load_cert_chain(certfile=certfile_path, keyfile=keyfile_path)


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
# app.allowed_hosts = ["http://e3-ilt-app-api.us-east-1.elasticbeanstalk.com"]
# app.add_middleware(HTTPSRedirectMiddleware)
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc):
    
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
# origins = ["http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["HTTPS"],
)
# app.add_middleware(TrustedHostMiddleware, 
#                    allowed_hosts=["http://middle-ilt-app-ui-env.eba-3gvras9p.us-east-1.elasticbeanstalk.com", "127.0.0.1"])

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

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=443, reload=True,
#                                 ssl_keyfile=keyfile_path,
#                                 ssl_certfile= certfile_path,
#                                 workers=4)