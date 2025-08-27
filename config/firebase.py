# config/firebase.py

import firebase_admin
from firebase_admin import credentials, firestore
import logging

logger = logging.getLogger(__name__)
db = None

def init_firebase():
    """
    يهيئ Firebase باستخدام بيانات الاعتماد الافتراضية للتطبيق (ADC).
    هذه الطريقة تعمل محلياً (بعد gcloud auth) وفي بيئة Google Cloud (App Engine, etc.).
    """
    global db
    
    # تحقق مما إذا كان التطبيق قد تم تهيئته بالفعل لتجنب الأخطاء
    if not firebase_admin._apps:
        try:
            logger.info("☁️ Initializing Firebase using Application Default Credentials...")
            
            # هذه هي الطريقة الموصى بها. لا تحتاج إلى ملفات JSON أو متغيرات بيئة للمفاتيح.
            # هي تستخدم حساب الخدمة تلقائياً في App Engine.
            cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred, {
                'projectId': 'whatsapp-bot-dashboard', # <-- ضع معرف المشروع هنا
            })
            
            logger.info("✅ Firebase initialized successfully!")
            db = firestore.client()

        except Exception as e:
            logger.critical(f"❌ FAILED to initialize Firebase: {e}", exc_info=True)
            db = None
    else:
        # إذا كان مهيأ بالفعل، فقط احصل على العميل
        if not db:
            db = firestore.client()

# قم باستدعاء الدالة عند استيراد الملف
init_firebase()
