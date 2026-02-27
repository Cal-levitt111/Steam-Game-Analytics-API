from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserRead
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> UserRead:
    user = register_user(db, email=payload.email, password=payload.password, display_name=payload.display_name)
    response.headers['Location'] = f'/api/v1/auth/users/{user.id}'
    return UserRead.model_validate(user)


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    _, token = login_user(db, email=payload.email, password=payload.password)
    return TokenResponse(access_token=token)