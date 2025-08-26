from config.firebase import db
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class FirestoreRepository:
    def __init__(self):
        self.users_collection = None
        if db:
            self.users_collection = db.collection("users")
        else:
            logger.warning("Firestore not available - using in-memory storage for development")
            self.users = []  # تخزين مؤقت في الذاكرة للتطوير
        
    def get_user_by_email(self, email: str) -> Optional[dict]:
        try:
            if self.users_collection:
                query = self.users_collection.where("email", "==", email).limit(1)
                docs = query.stream()
                for doc in docs:
                    return {"id": doc.id, **doc.to_dict()}
                return None
            else:
                # البحث في التخزين المؤقت
                for user in self.users:
                    if user.get("email") == email:
                        return user
                return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        try:
            if self.users_collection:
                doc = self.users_collection.document(user_id).get()
                if doc.exists:
                    return {"id": doc.id, **doc.to_dict()}
                return None
            else:
                # البحث في التخزين المؤقت
                for user in self.users:
                    if user.get("id") == user_id:
                        return user
                return None
        except Exception as e:
            logger.error(f"Error getting user by id: {str(e)}")
            return None
    
    def create_user(self, email: str, password: str, role: str = "user") -> str:
        try:
            hashed_password = pwd_context.hash(password)
            user_data = {
                "email": email,
                "password_hash": hashed_password,
                "role": role,
                "subscription_expiry": None,
                "created_at": datetime.now()
            }
            
            if self.users_collection:
                doc_ref = self.users_collection.add(user_data)
                return doc_ref[1].id
            else:
                # إضافة إلى التخزين المؤقت
                user_id = str(len(self.users) + 1)
                user_data["id"] = user_id
                self.users.append(user_data)
                return user_id
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise Exception(f"Error creating user: {str(e)}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def update_subscription_expiry(self, user_id: str, expiry_date: datetime) -> bool:
        try:
            if self.users_collection:
                self.users_collection.document(user_id).update({
                    "subscription_expiry": expiry_date
                })
                return True
            else:
                # تحديث في التخزين المؤقت
                for user in self.users:
                    if user.get("id") == user_id:
                        user["subscription_expiry"] = expiry_date
                        return True
                return False
        except Exception as e:
            logger.error(f"Error updating subscription: {str(e)}")
            return False
    
    def get_all_users(self) -> List[dict]:
        try:
            if self.users_collection:
                docs = self.users_collection.stream()
                users = []
                for doc in docs:
                    user_data = doc.to_dict()
                    users.append({
                        "id": doc.id,
                        "email": user_data.get("email"),
                        "role": user_data.get("role"),
                        "subscription_expiry": user_data.get("subscription_expiry")
                    })
                return users
            else:
                # إرجاع جميع المستخدمين من التخزين المؤقت
                return self.users.copy()
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []

firestore_repo = FirestoreRepository()