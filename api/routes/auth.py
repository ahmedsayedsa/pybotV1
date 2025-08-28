# api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

# --- المسارات الصحيحة للاستيراد ---
from repositories.firestore_repo import get_user_by_email, verify_password
# افترض أن لديك ملفاً لإنشاء التوكن
# from .token_utils import create_access_token 

router = APIRouter()
templates = Jinja2Templates(directory="public")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/token") # هذا هو الـ endpoint الذي يستقبله الفورم
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_email(form_data.username)
    
    # التحقق من وجود المستخدم ومن صحة كلمة المرور
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # إذا نجح التحقق، قم بإنشاء توكن
    # access_token = create_access_token(data={"sub": user.email})
    # return {"access_token": access_token, "token_type": "bearer"}
    
    # مؤقتاً، سنرجع رسالة نجاح
    return {"message": "Login successful!", "user_role": user.role}

# ... باقي المسارات الخاصة بالـ auth ...
