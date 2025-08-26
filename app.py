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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="WhatsApp Subscription Management", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# استيراد المسارات من الموقع الصحيح (بدون src.)
try:
    from api.routes import auth, admin, user
    app.include_router(auth.router)
    app.include_router(admin.router)
    app.include_router(user.router)
    logger.info("API routes loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load API routes: {e}")

# محاولة تهيئة Firebase
try:
    from config.firebase import init_firebase
    init_firebase()
    logger.info("Firebase initialized successfully")
except ImportError as e:
    logger.warning(f"Could not initialize Firebase: {e}")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")

# خدمة الملفات الثابتة
if os.path.exists("public"):
    app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    return {"status": "healthy", "version": "1.0.0"}

# خدمة صفحات HTML
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)