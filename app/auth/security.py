"""
Authentication utilities and security functions
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User, UserRole


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username and password
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode JWT token
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def get_current_user_info(token: str) -> dict:
    """
    Extract user information from JWT token
    """
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    role: str = payload.get("role")
    
    if user_id is None or role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return {"user_id": user_id, "role": role}


def require_role(user_role: str, required_roles: list) -> bool:
    """
    Check if user has required role
    """
    return user_role in required_roles


def get_pm_required_exception() -> HTTPException:
    """
    Return exception for project manager role requirement
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Project Manager role required"
    )


def get_resource_not_found_exception(resource: str = "resource") -> HTTPException:
    """
    Return exception for resource not found
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found"
    )


def get_access_denied_exception() -> HTTPException:
    """
    Return exception for access denied
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


# Role-based access control decorators (for FastAPI dependencies)
def is_project_manager(role: str) -> bool:
    """Check if user is project manager"""
    return role == UserRole.PROJECT_MANAGER


def is_backend_developer(role: str) -> bool:
    """Check if user is backend developer"""
    return role == UserRole.BACKEND_DEVELOPER