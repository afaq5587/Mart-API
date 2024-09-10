from fastapi import FastAPI, Depends
from sqlmodel import Session
from contextlib import asynccontextmanager
from app.config.db import create_tables, get_session
from app.router.auth import auth_router
from app.router.user import user_router
# from app.kafka.producer_consumer import kafka_consumer

# from app.models.user_model import User, Register_User
# from app.utils.get_user import get_user_from_db
# from app.utils.security import hash_password
# from typing import Annotated


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app: FastAPI = FastAPI(
    lifespan=lifespan,
    title="User Microservice",
    version="1.0.0",
    root_path="/user-service",
    root_path_in_servers=True,
    servers=[
        {
            "url": "http://127.0.0.1:8000",
            "description": "User Service's Development Server",
        }
    ],
)

app.include_router(router=auth_router)
app.include_router(router=user_router)

@app.get("/")
async def user_service():
    return {"message": "Welcome to user service."}
