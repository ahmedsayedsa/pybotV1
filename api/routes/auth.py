from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt
from src.models.schemas import UserCreate, UserResponse, Token
from src.repositories.firestore_repo import firestore_repo
from src.config.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    existing_user = firestore_repo.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = firestore_repo.create_user(user.email, user.password)
    new_user = firestore_repo.get_user_by_id(user_id)
    
    return UserResponse(
        id=new_user["id"],
        email=new_user["email"],
        role=new_user["role"],
        subscription_expiry=new_user.get("subscription_expiry")
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = firestore_repo.get_user_by_email(form_data.username)
    if not user or not firestore_repo.verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(hours=24)
    )
    
    return Token(access_token=access_token, token_type="bearer")