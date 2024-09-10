from sqlmodel import Session, select
from app.config.db import get_session
from app.models.user_model import User
from typing import Annotated, Any
from fastapi import Depends


def get_user_from_db(
    session: Annotated[Session, Depends(get_session)],
    username: str | None = None,
    email: str | Any = None,
):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if user:
            return user
    return user
