# app.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging

# --- إعدادات الـ Logging (مهمة جداً للتشخيص) ---
# هذا يضمن أن الرسائل ستظهر في سجلات Google Cloud Run
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("-----> [STARTUP] Application script starting...")

# --- تهيئة التطبيق والـ Limiter ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="WhatsApp Subscription Management", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- إعدادات الـ Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

logger.info("-----> [STARTUP] Middleware configured.")

# --- استيراد وربط المسارات (Routers) ---
try:
    from api.routes import auth, admin, user
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(user.router)
    logger.info("-----> [STARTUP] API routes loaded successfully.")
except ImportError as e:
    # هذا سيخبرنا بالضبط إذا فشل استيراد أي مسار
    logger.critical(f"-----> [FATAL STARTUP ERROR] Could not load API routes: {e}", exc_info=True)
    # في حالة الفشل، قد نرغب في الخروج لمنع الحاوية من العمل بشكل غير صحيح
    raise e

# --- تهيئة Firebase ---
try:
    # نفترض أن هذا الملف يقوم بالتهيئة عند استيراده
    from config.firebase import db
    if db:
        logger.info("-----> [STARTUP] Firebase initialized successfully.")
    else:
        logger.warning("-----> [STARTUP] Firebase module loaded, but 'db' object is None.")
except Exception as e:
    logger.critical(f"-----> [FATAL STARTUP ERROR] Failed to initialize Firebase: {e}", exc_info=True)
    raise e

# --- خدمة الملفات الثابتة (Static Files) ---
if os.path.exists("public"):
    app.mount("/static", StaticFiles(directory="public"), name="static")
    logger.info("-----> [STARTUP] Static files mounted from 'public' directory.")

# --- نقاط النهاية (Endpoints) الأساسية ---
@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    return {"status": "healthy", "version": "1.0.0"}

# خدمة صفحات HTML
# (الكود الخاص بك هنا سليم)
if os.path.exists("public/login.html"):
    @app.get("/", response_class=HTMLResponse)
    async def serve_login():
        with open("public/login.html", "r") as f:
            return HTMLResponse(content=f.read())

if os.path.exists("public/admin.html"):
    @app.get("/admin", response_class=HTMLResponse)
    async def serve_admin():
        with open("public/admin.html", "r") as f:
            return HTMLResponse(content=f.read())

if os.path.exists("public/user.html"):
    @app.get("/user", response_class=HTMLResponse)
    async def serve_user():
        with open("public/user.html", "r") as f:
            return HTMLResponse(content=f.read())

logger.info("-----> [STARTUP] HTML routes configured.")

# --- نقطة الدخول لتشغيل Uvicorn (للتطوير المحلي) ---
if __name__ == "__main__":
    import uvicorn
    logger.info("-----> [STARTUP] Running in local development mode with Uvicorn.")
    uvicorn.run(app, host="0.0.0.0", port=8080)
else:
    # هذه الرسالة ستظهر عند التشغيل عبر Gunicorn في Cloud Run
    logger.info("-----> [STARTUP] Application startup sequence complete. Handing over to Gunicorn/Uvicorn worker.")

