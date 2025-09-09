# config/settings.py

import os
from dotenv import load_dotenv

# يقوم بتحميل متغيرات البيئة من ملف .env (مهم للتطوير المحلي)
load_dotenv()

class Settings:
    """
    يحتوي على جميع إعدادات التطبيق.
    يقرأ القيم من متغيرات البيئة أولاً، ثم يستخدم قيمة افتراضية إذا لم يجدها.
    """
    project_name: str = "WhatsApp Subscription Management"
    version: str = "1.0.0"

    # --- هذا هو الجزء الأهم ---
    # يقرأ المفتاح السري من متغير البيئة JWT_SECRET
    jwt_secret: str = os.getenv("JWT_SECRET")
    
    # تأكد من أن لديك متغيرات أخرى مثل الخوارزمية إذا كنت تستخدمها
    # algorithm: str = os.getenv("ALGORITHM", "HS256")

    # --- تحقق حيوي ---
    if not jwt_secret:
        raise ValueError("FATAL ERROR: JWT_SECRET environment variable is not set.")

# إنشاء نسخة واحدة من الإعدادات لاستخدامها في جميع أنحاء التطبيق
settings = Settings()
 