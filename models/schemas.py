from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: str  # Changed from EmailStr to str
    password: str

class UserLogin(BaseModel):
    email: str  # Changed from EmailStr to str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str  # Changed from EmailStr to str
    role: str
    subscription_expiry: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    user_id: str
    expiry_date: datetime