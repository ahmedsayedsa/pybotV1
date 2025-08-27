from google.cloud import firestore
from datetime import datetime, timezone

project_id = "whatsapp-bot-dashboard"

try:
    # سيستخدم بيانات الاعتماد التي قمت بحفظها تلقائياً
    db = firestore.Client(project=project_id)
    print(f"✅ Successfully connected to Firestore project: {project_id}")

    doc_ref = db.collection("users").document("admin-user")

    user_data = {
        "email": "ahmedhell13@gmail.com",
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "role": "admin",
        "subscription_expiry": datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        "created_at": datetime.now(timezone.utc)
    }

    doc_ref.set(user_data)
    print("======================================================")
    print("✅ User 'admin-user' created/updated successfully!")
    print("======================================================")

except Exception as e:
    print("❌ An error occurred:")
    print(e)
