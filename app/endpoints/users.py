"""Module with endpoints for user"""

from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.depends import get_auth_service, get_user_service, get_db
from app.schemas.users import User, UserCreate, UserDetail, UserUpdate, UserDelete, Token
from app.schemas.base import HTTPNotFoundError, NotAuthenticatedError
from app.services.users import UserService
from app.services.auth import AuthService
from app.settings import setting
from app.utils.users import get_current_user


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


DBAsyncSession = Annotated[AsyncSession, Depends(get_db)]
AuthenticateService = Annotated[AuthService, Depends(get_auth_service)]
MainUserService = Annotated[UserService, Depends(get_user_service)]


@auth_router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    async_session: DBAsyncSession,
    auth_service: AuthenticateService
):
    """Login endpoint"""
    user = await auth_service.authenticate_user(
        async_session,
        form_data.username,
        form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/signin", response_model=UserDetail)
async def create_new_user(
    user: UserCreate,
    user_service: MainUserService,
    async_session: DBAsyncSession,
    auth_service: AuthenticateService
):
    """Endpoint for create user"""
    db_user = await user_service.get_user_by_username(async_session, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already exists"
        )
    hashed_password = auth_service.get_password_hash(user.password)
    new_user = await user_service.create_user(
        async_session=async_session,
        username=user.username,
        email=user.email,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        avatar=user.avatar,
        about=user.about
    )
    return new_user


@user_router.get("/", response_model=list[User])
async def get_all_users(
    async_session: DBAsyncSession,
    user_service: MainUserService,
    skip: int = 0,
    limit: int = 100
):
    """Endpoint for getting all users"""
    return await user_service.get_users(async_session, skip, limit)


@user_router.get(
    "/me",
    response_model=UserDetail,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": NotAuthenticatedError}
    }
)
async def get_user_profile(current_user: Annotated[UserDetail, Depends(get_current_user)]):
    """Endpoint for getting your profile"""
    return current_user


@user_router.put(
    "/me",
    response_model=UserDetail,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": NotAuthenticatedError},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"}
    }
)
async def update_user_profile(
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    async_session: DBAsyncSession,
    user_service: MainUserService,
    data: UserUpdate
):
    """Endpoint for update user profile"""
    user = await user_service.update_user(
        async_session,
        current_user.id,
        data.model_dump(),
        current_user
    )
    return user


@user_router.delete(
    "/me",
    response_model=UserDelete,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": NotAuthenticatedError},
    }
)
async def delete_account(
    current_user: Annotated[UserDetail, Depends(get_current_user)],
    async_session: DBAsyncSession,
    user_service: MainUserService
):
    """Endpoint for delete user profile"""
    await user_service.delete_user(async_session, current_user.id)
    data = {"message": "User has been deleted successfully"}
    return JSONResponse(content=data, status_code=status.HTTP_200_OK)


@user_router.get(
    "/{user_id}",
    response_model=UserDetail,
    responses={
        status.HTTP_200_OK: {"model": UserDetail},
        status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}
    }
)
async def get_user_detail(
    async_session: DBAsyncSession,
    user_service: MainUserService,
    user_id: UUID
):
    """Endpoint for getting user profile"""
    return await user_service.get_user_by_id(async_session, user_id)
