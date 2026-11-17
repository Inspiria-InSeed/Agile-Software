from typing import Optional, List

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db.models import User as UserModel
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_id(db: Session, *, user_id: int) -> Optional[UserModel]:
    """
    Retrieve an entity from the database by primary key.

    Args:
        db: SQLAlchemy session.
        user_id: Primary key of the user.

    Returns:
        UserModel instance if found, None otherwise.
    """
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_user_by_email(db: Session, *, email: str) -> Optional[UserModel]:
    """
    Retrieve an entity from the database by email address.

    Args:
        db: SQLAlchemy session.
        email: Email address of the user.

    Returns:
        UserModel instance if found, None otherwise.
    """
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_multi_users(
    db: Session, *, skip: int = 0, limit: int = 100
) -> List[UserModel]:
    """
    Retrieve multiple user entities with optional pagination.

    Args:
        db: SQLAlchemy session.
        skip: Number of records to skip.
        limit: Max number of records to return.

    Returns:
        List of UserModel objects.
    """
    return db.query(UserModel).offset(skip).limit(limit).all()


def create_user(db: Session, *, obj_in: UserCreate) -> UserModel:
    """
    Create a new user entry in the database.

    Args:
        db: SQLAlchemy session.
        obj_in: Pydantic creation schema.

    Returns:
        Newly created UserModel instance.
    """
    hashed_password = get_password_hash(obj_in.password)
    db_obj = UserModel(
        email=obj_in.email,
        hashed_password=hashed_password,
        full_name=obj_in.full_name,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_user(
    db: Session, *, db_obj: UserModel, obj_in: UserUpdate
) -> UserModel:
    """
    Update an existing user entry in the database.

    Args:
        db: SQLAlchemy session.
        db_obj: Existing UserModel instance.
        obj_in: Pydantic update schema or dict.

    Returns:
        Updated UserModel instance.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)

    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def authenticate_user(
    db: Session, *, email: str, password: str
) -> Optional[UserModel]:
    """
    Authenticate a user by email and password.

    Args:
        db: SQLAlchemy session.
        email: User email.
        password: Plain text password.

    Returns:
        UserModel instance if authenticated, None otherwise.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user