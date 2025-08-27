# api/routes/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import logging

# تأكد من أن هذه المسارات صحيحة
from models.schemas import UserResponse, SubscriptionUpdate
from repositories.firestore_repo import firestore_repo
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    "حارس" أمني يتحقق من التوكن ويضمن أن المستخدم هو أدمن.
    """
    logger.info("ADMIN_AUTH_DEBUG: Attempting to authorize admin via Bearer Token.")
    token = credentials.credentials
    logger.info(f"ADMIN_AUTH_DEBUG: SUCCESS - Found Bearer Token. Starts with: {token[:15]}...")
    
    try:
        logger.info("ADMIN_AUTH_DEBUG: Attempting to decode JWT...")
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_role = payload.get("role")
        logger.info(f"ADMIN_AUTH_DEBUG: SUCCESS - JWT decoded. Payload role is: '{user_role}'")

        if user_role != "admin":
            logger.error(f"ADMIN_AUTH_DEBUG: FAILED - User role '{user_role}' is not 'admin'. Access denied.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        logger.info("ADMIN_AUTH_DEBUG: SUCCESS - Authorization complete. User is an admin.")
        return payload
        
    except jwt.PyJWTError as e:
        logger.critical(f"ADMIN_AUTH_DEBUG: FAILED - JWT decoding failed. Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}"
        )

@router.get("/users", response_model=list[UserResponse])
async def get_all_users(current_admin: dict = Depends(get_current_admin)):
    users = firestore_repo.get_all_users()
    return [
        UserResponse(
            id=user["id"],
            email=user["email"],
            role=user["role"],
            subscription_expiry=user.get("subscription_expiry")
        )
        for user in users
    ]

@router.patch("/subscription")
async def update_subscription(
    subscription_update: SubscriptionUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    user = firestore_repo.get_user_by_id(subscription_update.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    success = firestore_repo.update_subscription_expiry(
        subscription_update.user_id,
        subscription_update.expiry_date
    )
    
    if success:
        return {"message": "Subscription updated successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update subscription")
