from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UpdateMeRequest, UserRead
from app.services.auth_service import login_user, register_user, update_current_user

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, response: Response, db: Session = Depends(get_db)) -> UserRead:
    user = register_user(
        db,
        email=payload.email,
        password=payload.password,
        display_name=payload.display_name,
        client_ip=request.client.host if request.client else None,
    )
    response.headers['Location'] = f'/api/v1/auth/users/{user.id}'
    return UserRead.model_validate(user)


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    _, token = login_user(
        db,
        email=payload.email,
        password=payload.password,
        client_ip=request.client.host if request.client else None,
    )
    return TokenResponse(access_token=token)


@router.get('/me', response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


@router.put('/me', response_model=UserRead)
def update_me(
    payload: UpdateMeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    user = update_current_user(
        db,
        current_user,
        display_name=payload.display_name,
        new_password=payload.password,
    )
    return UserRead.model_validate(user)
