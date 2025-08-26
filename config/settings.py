from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
import os
from typing import Optional

class Settings(BaseSettings):
    port: int = Field(8080, env="PORT")
    jwt_secret: Optional[str] = Field(None, env="JWT_SECRET")  # جعلها اختيارية
    firebase_project_id: str = Field("chrome-backbone-458221-m9", env="FIREBASE_PROJECT_ID")
    firebase_client_email: str = Field("firebase-adminsdk@chrome-backbone-458221-m9.iam.gserviceaccount.com", env="FIREBASE_CLIENT_EMAIL")
    firebase_private_key: Optional[str] = Field(None, env="FIREBASE_PRIVATE_KEY")  # جعلها اختيارية
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()