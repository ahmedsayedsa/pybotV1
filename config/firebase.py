# config/firebase.py
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import logging

db = None

try:
    # الطريقة الأولى (للإنتاج مثل Railway): قراءة المتغير من البيئة
    creds_json_str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if creds_json_str:
        logging.info("Found GOOGLE_APPLICATION_CREDENTIALS_JSON env var. Initializing with JSON content.")
        creds_dict = json.loads(creds_json_str)
        cred = credentials.Certificate(creds_dict)
    else:
        # الطريقة الثانية (للتطوير المحلي أو VM): استخدام بيانات الاعتماد الافتراضية
        logging.info("Env var not found. Initializing with default credentials.")
        cred = credentials.ApplicationDefault()

    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logging.info("✅ Firebase Admin SDK initialized successfully. Firestore client is ready.")

except Exception as e:
    logging.error(f"❌ Failed to initialize Firebase Admin SDK: {e}", exc_info=True)

