from fastapi import Depends, HTTPException, status
from typing import Annotated
from sqlmodel import Session
from app.config.setting import SECRET_KEY, ALGORITHYM
from app.config.db import get_session
from jose import jwt, JWTError
from app.models.token_model import TokenData
from app.utils.get_user import get_user_from_db
from fastapi.security import OAuth2PasswordBearer

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def current_user(
    token: Annotated[str, Depends(oauth_scheme)],
    session: Annotated[Session, Depends(get_session)],
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, please login again",
        headers={"www-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHYM)
        username: str | None = payload.get("sub")

        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exception
    user = get_user_from_db(session, username=token_data.username)
    if not user:
        raise credential_exception
    return user


def validate_refresh_token(
    token: str,
    session: Annotated[Session, Depends(get_session)],
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, please login again",
        headers={"www-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHYM)
        email: str | None = payload.get("sub")

        if email is None:
            raise credential_exception
        token_data = TokenData(email=email)

    except JWTError:
        raise credential_exception
    user = get_user_from_db(session, email=token_data.email)
    if not user:
        raise credential_exception
    return user
