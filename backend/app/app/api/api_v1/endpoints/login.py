from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings

router = APIRouter()

# /login/token is used by web browser
@router.post("/login/token", response_model=schemas.Response, exclude_dependencies=True)
def login_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """Web Login Api"""
    user = security.authenticate_user(security.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(user.username, expires_delta=access_token_expires)
    return {
        "code": 20000,
        "data": {
            "token": access_token,
            "token_type": "bearer",
        },
        "message": "",
    }

# /login/access-token is used by RESTful API server
@router.post("/login/access-token", response_model=schemas.Token, exclude_dependencies=True)
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """OAuth2 compatible token login, get an access token for future requests"""
    user = security.authenticate_user(security.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(user.username, expires_delta=access_token_expires)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/logout", response_model=schemas.Response)
def logout() -> Any:
    """logout"""
    return {"code": 20000, "data": {"logout": True}, "message": "", }
