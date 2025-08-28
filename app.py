# app.py
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

# --- استيراد المسارات (Routes) من مجلد api ---
# تأكد من أن هذه المسارات صحيحة لمشروعك
from api.routes.auth import router as auth_router
from api.routes.admin import router as admin_router
from api.routes.user import router as user_router

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
app.mount("/public", StaticFiles(directory="public"), name="public")

# --- تضمين المسارات في التطبيق الرئيسي ---
logging.info("Including routers...")
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(user_router, prefix="/user", tags=["User"])
logging.info("Routers included successfully.")


# --- Endpoint سري ومؤقت لإنشاء الأدمن ---
@app.get("/setup/create_admin_user_secretly", tags=["Setup"])
async def create_admin_secretly():
    # الاستيراد داخل الدالة لتجنب أي مشاكل في بدء التشغيل
    from config.firebase import db
    from repositories.firestore_repo import pwd_context
    from google.cloud import firestore
    
    ADMIN_EMAIL = "ahmedhell13@gmail.com"
    ADMIN_PASSWORD = "123456"

    if not db:
        return {"status": "error", "message": "Firestore database not initialized."}

    try:
        logging.info(f"SECRET ENDPOINT: Attempting to create/update admin user: {ADMIN_EMAIL}")
        
        hashed_password = pwd_context.hash(ADMIN_PASSWORD)
        
        # --- هذا هو القسم الذي كان به الخطأ على الأرجح ---
        user_data = {
            'email': ADMIN_EMAIL,
            'password_hash': hashed_password,
            'role': 'admin',
            'subscription_expiry': None,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        # -------------------------------------------------
        
        user_ref = db.collection('users').document(ADMIN_EMAIL)
        user_ref.set(user_data, merge=True)
        
        logging.info(f"SECRET ENDPOINT: Admin user '{ADMIN_EMAIL}' created/updated successfully!")
        return {"status": "success", "message": f"Admin user {ADMIN_EMAIL} created/updated."}
    
    except Exception as e:
        logging.error(f"SECRET ENDPOINT ERROR: {e}", exc_info=True)
        return {"status": "error", "message": "An internal error occurred."}


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to PyBot V1 API. Visit /auth/login to start."}

logging.info("Application startup sequence complete. Ready to serve requests.")
