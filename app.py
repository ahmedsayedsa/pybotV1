# app.py

# ---------------------------------------------------------------------------
# 1. الاستيرادات الأساسية (Imports)
# ---------------------------------------------------------------------------
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# 2. إعداد السجلات (Logging) - خطوة حاسمة للتشخيص
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

logger.info("-----> [STARTUP] app.py script execution started.")

# ---------------------------------------------------------------------------
# 3. تهيئة تطبيق FastAPI والمكونات الأساسية
# ---------------------------------------------------------------------------
try:
    app = FastAPI(
        title="WhatsApp Subscription Management", 
        version="1.0.0",
        description="A FastAPI application for WhatsApp subscription management"
    )
    logger.info("-----> [STARTUP] FastAPI app initialized.")
except Exception as e:
    logger.critical(f"-----> [FATAL STARTUP ERROR] Failed to initialize FastAPI: {e}", exc_info=True)
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
# 5. نقاط النهاية (Endpoints) الأساسية
# ---------------------------------------------------------------------------
@app.get("/", tags=["Root"])
async def root():
    """صفحة البداية الأساسية."""
    return {
        "message": "WhatsApp Subscription Management API", 
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """نقطة نهاية بسيطة للتحقق من أن التطبيق يعمل."""
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "message": "Application is running successfully"
    }

@app.get("/test", tags=["Test"])
async def test_endpoint():
    """نقطة اختبار بسيطة."""
    return {
        "message": "FastAPI is working perfectly!", 
        "status": "success",
        "timestamp": "2025-08-27"
    }

# ---------------------------------------------------------------------------
# 6. استيراد وربط المسارات (Routers) - مع معالجة الأخطاء
# ---------------------------------------------------------------------------
routes_loaded = []

try:
    from api.routes import auth
    app.include_router(auth.router)
    routes_loaded.append("auth")
    logger.info("-----> [STARTUP] Auth routes loaded successfully.")
except ImportError as e:
    logger.warning(f"-----> [STARTUP WARNING] Could not load auth routes: {e}")
except Exception as e:
    logger.error(f"-----> [STARTUP ERROR] Error loading auth routes: {e}")

try:
    from api.routes import admin
    app.include_router(admin.router)
    routes_loaded.append("admin")
    logger.info("-----> [STARTUP] Admin routes loaded successfully.")
except ImportError as e:
    logger.warning(f"-----> [STARTUP WARNING] Could not load admin routes: {e}")
except Exception as e:
    logger.error(f"-----> [STARTUP ERROR] Error loading admin routes: {e}")

try:
    from api.routes import user
    app.include_router(user.router)
    routes_loaded.append("user")
    logger.info("-----> [STARTUP] User routes loaded successfully.")
except ImportError as e:
    logger.warning(f"-----> [STARTUP WARNING] Could not load user routes: {e}")
except Exception as e:
    logger.error(f"-----> [STARTUP ERROR] Error loading user routes: {e}")

logger.info(f"-----> [STARTUP] Routes loaded: {routes_loaded}")

# ---------------------------------------------------------------------------
# 7. تهيئة Firebase - مع معالجة الأخطاء
# ---------------------------------------------------------------------------
db = None
try:
    from config.firebase import db as firebase_db
    db = firebase_db
    if db:
        logger.info("-----> [STARTUP] Firebase connection established successfully.")
    else:
        logger.warning("-----> [STARTUP] Firebase module loaded, but 'db' object is None.")
except ImportError as e:
    logger.warning(f"-----> [STARTUP WARNING] Could not import Firebase config: {e}")
except Exception as e:
    logger.error(f"-----> [STARTUP ERROR] Firebase initialization error: {e}")

# ---------------------------------------------------------------------------
# 8. خدمة الملفات الثابتة (Static Files)
# ---------------------------------------------------------------------------
if os.path.exists("public"):
    try:
        app.mount("/static", StaticFiles(directory="public"), name="static")
        logger.info("-----> [STARTUP] Static files mounted from 'public' directory.")
    except Exception as e:
        logger.error(f"-----> [STARTUP ERROR] Failed to mount static files: {e}")
else:
    logger.warning("-----> [STARTUP] 'public' directory not found. Static files will not be served.")

# ---------------------------------------------------------------------------
# 9. خدمة صفحات HTML - مع معالجة الأخطاء
# ---------------------------------------------------------------------------
@app.get("/login", response_class=HTMLResponse, tags=["HTML"])
async def serve_login():
    """خدمة صفحة تسجيل الدخول."""
    try:
        if os.path.exists("public/login.html"):
            with open("public/login.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            raise HTTPException(status_code=404, detail="Login page not found")
    except Exception as e:
        logger.error(f"Error serving login page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/admin", response_class=HTMLResponse, tags=["HTML"])
async def serve_admin():
    """خدمة صفحة الأدمن."""
    try:
        if os.path.exists("public/admin.html"):
            with open("public/admin.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            raise HTTPException(status_code=404, detail="Admin page not found")
    except Exception as e:
        logger.error(f"Error serving admin page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/user", response_class=HTMLResponse, tags=["HTML"])
async def serve_user():
    """خدمة صفحة المستخدم."""
    try:
        if os.path.exists("public/user.html"):
            with open("public/user.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        else:
            raise HTTPException(status_code=404, detail="User page not found")
    except Exception as e:
        logger.error(f"Error serving user page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ---------------------------------------------------------------------------
# 10. معالج الأخطاء العام
# ---------------------------------------------------------------------------
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"message": "Page not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "path": str(request.url)}
    )

logger.info("-----> [STARTUP] HTML routes and error handlers configured.")

# ---------------------------------------------------------------------------
# 11. نقطة الدخول لتشغيل Uvicorn (للتطوير المحلي فقط)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    logger.info("-----> [STARTUP] Running in local development mode with Uvicorn.")
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
else:
    # هذه الرسالة ستظهر عند التشغيل عبر Gunicorn في Cloud Run
    logger.info("-----> [STARTUP] Application startup sequence complete. Ready to serve requests.")
    logger.info(f"-----> [STARTUP] Available routes loaded: {routes_loaded}")
    logger.info(f"-----> [STARTUP] Firebase status: {'Connected' if db else 'Not connected'}")