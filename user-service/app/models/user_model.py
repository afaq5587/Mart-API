from sqlmodel import SQLModel, Field
from typing import Optional, Annotated
from app.models.roles import UserRole
from pydantic import BaseModel
from fastapi import Form


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None, index=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=20)
    email: str = Field(unique=True, index=True)
    password: str = Field(default=None)
    role: UserRole = Field(default=UserRole.user)
    is_allowed: bool = Field(default=True)


class Register_User(BaseModel):
    username: Annotated[str, Form()]
    email: Annotated[str, Form()]
    password: Annotated[str, Form()]


class User_Profile(BaseModel):
    username: str
    email: str


class Forgot_Password(BaseModel):
    email: Annotated[str, Form()]


class Reset_Password(BaseModel):
    new_password: Annotated[str, Form()]
    confirm_password: Annotated[str, Form()]


class Change_Email(BaseModel):
    new_email: Annotated[str, Form()]


class Edit_User(BaseModel):
    username: Annotated[Optional[str], Form()]
    email: Annotated[Optional[str], Form()]
    password: Annotated[Optional[str], Form()]
