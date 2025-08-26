import firebase_admin
from firebase_admin import credentials, firestore
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

def init_firebase():
    try:
        if not firebase_admin._apps:
            # تنظيف المفتاح من الأحرف الزائدة
            private_key = settings.firebase_private_key
            if private_key.startswith('"') and private_key.endswith('"'):
                private_key = private_key[1:-1]
            private_key = private_key.replace('\\n', '\n')
            
            cred = credentials.Certificate({
                "project_id": settings.firebase_project_id,
                "client_email": settings.firebase_client_email,
                "private_key": private_key
            })
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        return firestore.client()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        raise Exception(f"Failed to initialize Firebase: {str(e)}")

db = init_firebase()