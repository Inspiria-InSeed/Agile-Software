from typing import Generator, Optional

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db import models
from app.db.session import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/users/login/access-token",
    auto_error=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a SQLAlchemy database session.
    Yields a session and ensures it's closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_optional_current_user(
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
    session_token: str | None = Cookie(default=None, alias="inseed_session"),
) -> Optional[models.User]:
    token = token or session_token
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        user_id_int = int(user_id)
    except (JWTError, TypeError, ValueError):
        return None
    return db.query(models.User).filter(models.User.id == user_id_int).first()


def get_current_user(
    current_user: Optional[models.User] = Depends(get_optional_current_user),
) -> models.User:
    """Require a valid bearer token or browser session cookie."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user