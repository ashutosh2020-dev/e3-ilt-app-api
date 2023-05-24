from pydantic import BaseSettings

class AppSettings(BaseSettings):
    app_name: str = "Middle ILT APP"
    app_version: str = "1.0.0"
    app_description: str = "ILT application"
    app_port: int = 80

settings = AppSettings()