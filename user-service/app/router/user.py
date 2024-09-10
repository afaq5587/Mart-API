from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from app.utils.verify_token import current_user, validate_refresh_token
from app.utils.send_email import send_verification_email
from app.utils.get_user import get_user_from_db
from app.utils.remove_space import remove_space
from app.config.db import get_session
from app.config.setting import (
    EXPIRY_TIME,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    DOMAIN_NAME,
    SERVICE,
    PREFIX,
)
from app.utils.security import hash_password
from app.utils.create_token import create_access_token
from app.models.user_model import (
    User,
    User_Profile,
    Forgot_Password,
    Reset_Password,
    Change_Email,
    Edit_User,
    Register_User,
)
from typing import Annotated
from datetime import timedelta


user_router = APIRouter(
    prefix="/user", tags=["user"], responses={404: {"description": "Not Found"}}
)


@user_router.get("/profile", response_model=User)
async def profile(
    current_user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_user = get_user_from_db(session, current_user.username, current_user.email)
    user: User_Profile = User_Profile(username=db_user.username, email=db_user.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user


@user_router.post("/forgot-password")
async def forgot_password(
    user_data: Annotated[Forgot_Password, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    if user_data:
        db_user = get_user_from_db(session, email=user_data.email)
        if not db_user:
            raise HTTPException(status_code=400, detail="Enter a valid email")
        user: User_Profile = User_Profile(
            username=db_user.username, email=db_user.email
        )
        if user:
            expire_time = timedelta(minutes=EXPIRY_TIME)
            token = create_access_token({"sub": user.email}, expire_time)
            print(SENDER_EMAIL, SENDER_PASSWORD)
            verification_link = (
                f"{DOMAIN_NAME}/{SERVICE}/{PREFIX}/verify-email?token={token}"
            )
            send_email = send_verification_email(user.email, verification_link)
            return {"send_email": send_email, "token": token}
            # print("Token: ", token)
            # return {"username": user.username, "email": user.email, "token": token}
    else:
        raise HTTPException(status_code=400, detail="Enter a valid email")


@user_router.get("/verify-email")
async def verify_email(
    session: Annotated[Session, Depends(get_session)], token: str = Query(...)
):
    db_user = validate_refresh_token(token, session)
    user: User_Profile = User_Profile(username=db_user.username, email=db_user.email)
    if user:
        url: str = f"/{SERVICE}/{PREFIX}/reset-password?token={token}"
        return RedirectResponse(url=url)
    raise HTTPException(status_code=400, detail="Enter a valid email")


@user_router.patch("/reset-password")
async def reset_password(
    user_data: Annotated[Reset_Password, Depends()],
    session: Annotated[Session, Depends(get_session)],
    token: str = Query(...),
):
    if user_data.new_password == user_data.confirm_password:
        db_user = validate_refresh_token(token, session)
        if db_user:
            db_user.password = hash_password(user_data.new_password)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user
        else:
            raise HTTPException(status_code=404, detail="Invalid token or credientials")
    raise HTTPException(
        status_code=400, detail="Your new password or confirm password are not same"
    )


@user_router.patch("/change-email")
async def change_email(
    user_data: Annotated[Change_Email, Depends()],
    current_user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_user = get_user_from_db(session, email=current_user.email)
    if db_user:
        db_user.email = user_data.new_email
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")


@user_router.put("/edit-user")
async def edit_user(
    user_data: Annotated[Edit_User, Depends()],
    current_user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_user = get_user_from_db(session, current_user.username, current_user.email)
    # user: Edit_User = Edit_User(
    #     username=db_user.username, email=db_user.email, password=db_user.password
    # )
    if db_user:
        db_user.username = user_data.username
        db_user.email = user_data.email
        db_user.password = hash_password(user_data.password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")


@user_router.delete("/delete-user")
async def delete_user(
    current_user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    db_user = get_user_from_db(session, current_user.username, current_user.email)
    # user: User_Profile = User_Profile(username=db_user.username, email=db_user.email)
    if db_user:
        session.delete(db_user)
        session.commit()
        return {"message": f"User {db_user.username}'s account deleted successfully"}
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
