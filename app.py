# app.py

# ---------------------------------------------------------------------------
# 1. الاستيرادات الأساسية (Imports)
# ---------------------------------------------------------------------------
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# ---------------------------------------------------------------------------
# 2. إعداد السجلات (Logging) - خطوة حاسمة للتشخيص
# ---------------------------------------------------------------------------
# هذا يضمن أن الرسائل ستظهر في سجلات Google Cloud Run بشكل فوري وواضح
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("-----> [STARTUP] app.py script execution started.")

# ---------------------------------------------------------------------------
# 3. تهيئة تطبيق FastAPI والمكونات الأساسية
# ---------------------------------------------------------------------------
try:
    limiter = Limiter(key_func=get_remote_address)
    app = FastAPI(title="WhatsApp Subscription Management", version="1.0.0")
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("-----> [STARTUP] FastAPI app and rate limiter initialized.")
except Exception as e:
    logger.critical(f"-----> [FATAL STARTUP ERROR] Failed to initialize FastAPI or Limiter: {e}", exc_info=True)
    raise

# ---------------------------------------------------------------------------
# 4. إعدادات الـ Middleware
# ---------------------------------------------------------------------------
try:
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
    logger.info("-----> [STARTUP] Middleware (CORS, TrustedHost) configured.")
except Exception as e:
    logger.critical(f"-----> [FATAL STARTUP ERROR] Failed to configure middleware: {e}", exc_info=True)
    raise

# ---------------------------------------------------------------------------
# 5. استيراد وربط المسارات (Routers)
# ---------------------------------------------------------------------------
try:
    from api.routes import auth, admin, user
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(user.router)
    logger.info("-----> [STARTUP] API routes (auth, admin, user) loaded successfully.")
except ImportError as e:
    logger.critical(f"-----> [FATAL STARTUP ERROR] Could not load API routes: {e}", exc_info=True)
    raise

# ---------------------------------------------------------------------------
# 6. تهيئة Firebase
# ---------------------------------------------------------------------------
try:
    from config.firebase import db
    if db:
        logger.info("-----> [STARTUP] Firebase connection object 'db' imported successfully.")
    else:
        # هذا قد يشير إلى مشكلة في الاتصال أو الإعدادات
        logger.warning("-----> [STARTUP] Firebase module loaded, but 'db' object is None or False.")
except Exception as e:
    logger.critical(f"-----> [FATAL STARTUP ERROR] Failed to import or initialize Firebase: {e}", exc_info=True)
    raise

# ---------------------------------------------------------------------------
# 7. خدمة الملفات الثابتة (Static Files)
# ---------------------------------------------------------------------------
if os.path.exists("public"):
    app.mount("/static", StaticFiles(directory="public"), name="static")
    logger.info("-----> [STARTUP] Static files mounted from 'public' directory.")
else:
    logger.warning("-----> [STARTUP] 'public' directory not found. Static files will not be served.")

# ---------------------------------------------------------------------------
# 8. نقاط النهاية (Endpoints) الأساسية
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
@limiter.limit("10/minute")
async def health_check(request: Request):
    """نقطة نهاية بسيطة للتحقق من أن التطبيق يعمل."""
    return {"status": "healthy", "version": "1.0.0"}

# خدمة صفحات HTML
if os.path.exists("public/login.html"):
    @app.get("/", response_class=HTMLResponse, tags=["HTML"])
    async def serve_login():
        with open("public/login.html", "r") as f:
            return HTMLResponse(content=f.read())

if os.path.exists("public/admin.html"):
    @app.get("/admin", response_class=HTMLResponse, tags=["HTML"])
    async def serve_admin():
        with open("public/admin.html", "r") as f:
            return HTMLResponse(content=f.read())

if os.path.exists("public/user.html"):
    @app.get("/user", response_class=HTMLResponse, tags=["HTML"])
    async def serve_user():
        with open("public/user.html", "r") as f:
            return HTMLResponse(content=f.read())

logger.info("-----> [STARTUP] Root and HTML routes configured.")

# ---------------------------------------------------------------------------
# 9. نقطة الدخول لتشغيل Uvicorn (للتطوير المحلي فقط)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    logger.info("-----> [STARTUP] Running in local development mode with Uvicorn.")
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
else:
    # هذه الرسالة ستظهر عند التشغيل عبر Gunicorn في Cloud Run
    logger.info("-----> [STARTUP] Application startup sequence complete. Handing over to Gunicorn/Uvicorn worker.")
