import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, Union
import bcrypt
from jose import jwt
from app.core.config import settings


def _prepare_password_bytes(password: str) -> bytes:
    # Bcrypt strictly supports up to 72 bytes of password
    return password.encode("utf-8")[:72]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hashed password."""
    try:
        return bcrypt.checkpw(
            _prepare_password_bytes(plain_password),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash with auto-generated salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_prepare_password_bytes(password), salt)
    return hashed.decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    organization_id: str,
    permissions: List[str],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Issue signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "org_id": organization_id,
        "permissions": permissions,
        "type": "access",
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    organization_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Issue signed JWT refresh token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "org_id": organization_id,
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a signed JWT token."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
