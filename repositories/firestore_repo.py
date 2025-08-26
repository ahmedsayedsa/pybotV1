from google.cloud import firestore
from src.config.firebase import db
from passlib.context import CryptContext
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class FirestoreRepository:
    def __init__(self):
        self.users_collection = db.collection("users")
        logger.info("Firestore repository initialized")
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        try:
            query = self.users_collection.where("email", "==", email).limit(1)
            docs = query.stream()
            for doc in docs:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise Exception(f"Error getting user by email: {str(e)}")
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        try:
            doc = self.users_collection.document(user_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Error getting user by id: {str(e)}")
            raise Exception(f"Error getting user by id: {str(e)}")
    
    def create_user(self, email: str, password: str, role: str = "user") -> str:
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                raise Exception("User already exists")
                
            hashed_password = pwd_context.hash(password)
            user_data = {
                "email": email,
                "password_hash": hashed_password,
                "role": role,
                "subscription_expiry": None,
                "created_at": datetime.now()
            }
            doc_ref = self.users_collection.add(user_data)
            logger.info(f"User created successfully: {email}")
            return doc_ref[1].id
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise Exception(f"Error creating user: {str(e)}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def update_subscription_expiry(self, user_id: str, expiry_date: datetime) -> bool:
        try:
            self.users_collection.document(user_id).update({
                "subscription_expiry": expiry_date
            })
            logger.info(f"Subscription updated for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating subscription: {str(e)}")
            raise Exception(f"Error updating subscription: {str(e)}")
    
    def get_all_users(self) -> List[dict]:
        try:
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
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise Exception(f"Error getting all users: {str(e)}")

firestore_repo = FirestoreRepository()