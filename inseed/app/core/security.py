from datetime import datetime, timedelta
import base64
import hashlib
import hmac
import secrets
from typing import Any, Union

from jose import jwt

from app.core.config import settings

PASSWORD_HASH_ITERATIONS = 310_000


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The user's input password.
        hashed_password: The stored hashed password.

    Returns:
        True if the password matches, False otherwise.
    """
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        return False
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, salt, expected = hashed_password.split("$", 3)
            actual = hashlib.pbkdf2_hmac(
                "sha256",
                password_bytes,
                base64.urlsafe_b64decode(salt.encode("ascii")),
                int(iterations),
            )
            return hmac.compare_digest(
                actual, base64.urlsafe_b64decode(expected.encode("ascii"))
            )
        except (ValueError, TypeError):
            return False

    if hashed_password.startswith(("$2a$", "$2b$", "$2y$")):
        if len(password_bytes) > 72:
            return False
        try:
            import bcrypt

            return bcrypt.checkpw(password_bytes, hashed_password.encode("ascii"))
        except (ImportError, TypeError, ValueError):
            return False
    return False


def get_password_hash(password: str) -> str:
    """
    Generate a hash from a plain password.

    Args:
        password: The plain password to hash.

    Returns:
        The hashed password string.
    """
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("Password must be at most 72 bytes")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password_bytes, salt, PASSWORD_HASH_ITERATIONS
    )
    salt_text = base64.urlsafe_b64encode(salt).decode("ascii")
    digest_text = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${salt_text}${digest_text}"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Generate a JWT access token.

    Args:
        subject: The subject of the token (typically the user ID).
        expires_delta: Optional timedelta for token expiration.

    Returns:
        Encoded JWT token string.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt