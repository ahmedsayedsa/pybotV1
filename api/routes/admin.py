from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import jwt
from src.models.schemas import UserResponse, SubscriptionUpdate
from src.repositories.firestore_repo import firestore_repo
from src.config.settings import settings

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = firestore_repo.update_subscription_expiry(
        subscription_update.user_id,
        subscription_update.expiry_date
    )
    
    if success:
        return {"message": "Subscription updated successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )