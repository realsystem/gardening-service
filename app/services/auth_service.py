"""Authentication service"""
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings
from app.models.user import User
from app.repositories.user_repository import UserRepository

settings = get_settings()

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthService:
    """Service for authentication and authorization"""

    @staticmethod
    def _prepare_password(password: str) -> bytes:
        """
        Prepare password for bcrypt by pre-hashing with SHA256.
        Bcrypt has a 72-byte limit, so we always use SHA256 to ensure consistent behavior.
        """
        # Always hash with SHA256 first to avoid bcrypt 72-byte limit
        return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        prepared_password = AuthService._prepare_password(password)
        hashed = bcrypt.hashpw(prepared_password, bcrypt.gensalt())
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        try:
            prepared_password = AuthService._prepare_password(plain_password)
            return bcrypt.checkpw(prepared_password, hashed_password.encode('utf-8'))
        except Exception:
            # If verification fails for any reason, return False
            return False

    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        """
        Create a JWT access token.

        Timezone assumption: Uses UTC for token expiration timestamp.
        All JWT exp claims are in UTC as per JWT standard (RFC 7519).
        """
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "email": email,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password"""
        repo = UserRepository(db)
        user = repo.get_by_email(email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = None  # Will be injected by FastAPI
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Used in API endpoints to protect routes.
    """
    token = credentials.credentials
    payload = AuthService.decode_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = UserRepository(db)
    user = repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
