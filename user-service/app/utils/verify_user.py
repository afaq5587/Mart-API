from typing import Annotated
from sqlmodel import Session
from fastapi import Depends
from app.utils.security import verify_password
from app.utils.get_user import get_user_from_db
from app.config.db import get_session


def authenticate_user(
    username, password, session: Annotated[Session, Depends(get_session)]
):
    db_user = get_user_from_db(session, username=username)
    if not db_user:
        return False
    if not verify_password(password=password, hash_password=db_user.password):
        return False
    return db_user
