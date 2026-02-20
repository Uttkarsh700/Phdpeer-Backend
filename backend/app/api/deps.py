"""Shared API dependencies for authentication and authorization."""
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
import app.models  # noqa: F401
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve and return the authenticated user from a Bearer JWT."""
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized_exception

    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject = payload.get("sub")
        if not subject:
            raise unauthorized_exception
        user_id = UUID(str(subject))
    except (JWTError, ValueError):
        raise unauthorized_exception

    user_repository = UserRepository(db)
    user = user_repository.get_by_id(user_id)
    if not user or not user.is_active:
        raise unauthorized_exception

    return user


def require_roles(*allowed_roles: UserRole):
    """Dependency factory that enforces one of the provided roles."""

    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )
        return current_user

    return role_dependency
