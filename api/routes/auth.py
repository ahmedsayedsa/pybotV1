# api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Form
from typing import Annotated
from datetime import datetime, timedelta
import jwt

# تأكد من أن هذه المسارات صحيحة
from models.schemas import UserCreate, UserResponse, Token
from repositories.firestore_repo import firestore_repo
from config.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
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

# --- النسخة النهائية من دالة تسجيل الدخول ---
@router.post("/login", response_model=Token)
async def login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    """
    دالة تسجيل دخول مرنة تقبل البيانات المرسلة كـ form-data من المتصفح.
    هي تتوقع حقلاً اسمه 'username' وتستخدمه كـ email.
    """
    user = firestore_repo.get_user_by_email(username)
    
    # نستخدم الآن نفس طريقة التحقق من كلمة المرور من الكود الأصلي الخاص بك
    if not user or not firestore_repo.verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["id"], "role": user["role"]},
        expires_delta=timedelta(hours=24)
    )
    
    return Token(access_token=access_token, token_type="bearer")
