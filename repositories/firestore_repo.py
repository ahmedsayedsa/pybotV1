# repositories/firestore_repo.py

from passlib.context import CryptContext
from config.firebase import db # استيراد كائن قاعدة البيانات
from models.schemas import UserCreate, UserInDB # استيراد نماذج البيانات

# --- إعدادات تشفير كلمة المرور المركزية ---
# هذا هو مصدر الحقيقة الوحيد لكيفية تشفير والتحقق من كلمات المرور
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    يتحقق من تطابق كلمة المرور العادية مع النسخة المشفرة.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    يقوم بتشفير كلمة المرور.
    """
    return pwd_context.hash(password)

async def get_user_by_email(email: str) -> UserInDB | None:
    """
    يبحث عن مستخدم عن طريق البريد الإلكتروني ويعيده.
    """
    user_ref = db.collection('users').document(email)
    user_doc = await user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return UserInDB(**user_data)
    return None

# ... يمكنك إضافة دوال أخرى هنا مثل create_user إذا احتجت ...
