from fastapi import APIRouter, Response, status

from domain.services import CreateUserData
from domain.use_cases import register_user
from entrypoints.fastapi.schemas.request import UserRegisterRequestSchema


auth_router = APIRouter(tags=['Auth'], prefix='/auth')


@auth_router.post('/register')
async def register_handler(request_data: UserRegisterRequestSchema) -> Response:
    """Register new user"""
    data = CreateUserData.model_validate(request_data.model_dump(mode='json'))
    await register_user(data)
    return Response(status_code=status.HTTP_201_CREATED)
