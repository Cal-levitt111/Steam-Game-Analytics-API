from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repo import get_user_by_id

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppException(401, 'UNAUTHORIZED', 'Authentication credentials were not provided.')

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        error_code = str(exc)
        if error_code == 'TOKEN_EXPIRED':
            raise AppException(401, 'TOKEN_EXPIRED', 'Authentication token has expired.') from exc
        raise AppException(401, 'TOKEN_INVALID', 'Authentication token is invalid.') from exc

    subject = payload.get('sub')
    if subject is None:
        raise AppException(401, 'TOKEN_INVALID', 'Authentication token is invalid.')

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise AppException(401, 'TOKEN_INVALID', 'Authentication token is invalid.') from exc

    user = get_user_by_id(db, user_id)
    if user is None:
        raise AppException(401, 'TOKEN_INVALID', 'Authentication token is invalid.')
    return user