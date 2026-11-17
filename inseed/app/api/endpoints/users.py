from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import user as crud_user
from app.schemas import user as schema_user

router = APIRouter()


@router.get("/session", response_model=schema_user.User | None)
def read_browser_session(
    current_user: schema_user.User | None = Depends(deps.get_optional_current_user),
) -> Any:
    return current_user


@router.post("/login/session")
def create_browser_session(
    payload: schema_user.SessionLogin,
    request: Request,
    response: Response,
    db: Session = Depends(deps.get_db),
) -> dict[str, object]:
    user = crud_user.authenticate_user(db, email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = security.create_access_token(user.id)
    response.set_cookie(
        key="inseed_session",
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        path="/api",
    )
    return {"id": user.id, "email": user.email, "full_name": user.full_name}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(
        key="inseed_session",
        httponly=True,
        samesite="strict",
        path="/api",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/login/access-token", response_model=schema_user.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    return {
        "access_token": security.create_access_token(user.id),
        "token_type": "bearer",
    }


@router.get("/me", response_model=schema_user.User)
def read_user_me(
    current_user: schema_user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current logged in user.
    """
    return current_user


@router.post("/", response_model=schema_user.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schema_user.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
    user = crud_user.create_user(db, obj_in=user_in)
    return user


@router.get("/", response_model=List[schema_user.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: schema_user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve users. Only accessible to authenticated users.
    """
    users = crud_user.get_multi_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schema_user.User)
def read_user_by_id(
    user_id: int,
    current_user: schema_user.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by ID. Only accessible to authenticated users.
    """
    user = crud_user.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user