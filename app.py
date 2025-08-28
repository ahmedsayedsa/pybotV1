# app.py
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

# --- استيراد المسارات (Routes) من مجلد api ---
from api.routes.auth import router as auth_router
from api.routes.admin import router as admin_router
from api.routes.user import router as user_router # افترضت أن هذا هو المسار الثالث

# --- إعدادات التسجيل (Logging) ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(asctime)s %(message)s')

# --- إنشاء تطبيق FastAPI ---
app = FastAPI(title="PyBot V1")

# --- إعدادات CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- تحميل الملفات الثابتة (HTML, CSS, JS) ---
# مجلد public يحتوي على ملفات HTML
app.mount("/public", StaticFiles(directory="public"), name="public")

# --- تضمين المسارات في التطبيق الرئيسي ---
logging.info("Including routers...")
# لا يوجد public_router، الصفحات العامة قد تكون ضمن auth_router
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(user_router, prefix="/user", tags=["User"])
logging.info("Routers included successfully.")


# --- Endpoint سري ومؤقت لإنشاء الأدمن ---
@app.get("/setup/create_admin_user_secretly", tags=["Setup"])
async def create_admin_secretly():
    from config.firebase import db
    # --- المسار الصحيح لـ firestore_repo ---
    from repositories.firestore_repo import pwd_context
    from google.cloud import firestore
    
    ADMIN_EMAIL = "ahmedhell13@gmail.com"
    ADMIN_PASSWORD = "123456"

    if not db:
        return {"status": "error", "message": "Firestore database not initialized."}

    try:
        logging.info(f"SECRET ENDPOINT: Attempting to create/update admin user: {ADMIN_EMAIL}")
        hashed_password = pwd_context.hash(ADMIN_PASSWORD)
        
        user_data = {
            'email': ADMIN_EMAIL,
            'password_hash': hashed_password,
            'role': 'admin',
            'subscription_e
