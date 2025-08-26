from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os

class Settings(BaseSettings):
    port: int = Field(8080, env="PORT")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    firebase_project_id: str = Field("chrome-backbone-458221-m9", env="FIREBASE_PROJECT_ID")
    firebase_client_email: str = Field("firebase-adminsdk@chrome-backbone-458221-m9.iam.gserviceaccount.com", env="FIREBASE_CLIENT_EMAIL")
    firebase_private_key: str = Field(..., env="FIREBASE_PRIVATE_KEY")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()