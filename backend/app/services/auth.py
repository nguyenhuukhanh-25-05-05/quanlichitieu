from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash
from app.repositories.user import user_repository
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

class AuthService:
    def register(self, db: Session, *, user_in: UserCreate) -> User:
        db_user = user_repository.get_by_email(db, email=user_in.email)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email đã được đăng ký sử dụng.",
            )
        
        user_dict = user_in.model_dump()
        password = user_dict.pop("password")
        user_dict["hashed_password"] = get_password_hash(password)
        
        return user_repository.create(db, obj_in=user_dict)

    def authenticate(self, db: Session, *, email: str, password: str) -> User | None:
        user = user_repository.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

auth_service = AuthService()

# Dependency to get current authenticated user
async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
        token_data = TokenData(user_id=user_id)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception
        
    user = user_repository.get(db, id=token_data.user_id)
    if not user:
        raise credentials_exception
    return user
