from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.models.user_model import User, Register_User
from app.models.token_model import Token
from app.utils.get_user import get_user_from_db
from app.utils.security import hash_password
from app.utils.verify_user import authenticate_user
from app.utils.create_token import create_access_token
from app.utils.verify_token import validate_refresh_token
from app.config.db import get_session
from app.config.setting import (
    EXPIRY_TIME,
    ALGORITHYM,
    SECRET_KEY,
    BOOTSTRAP_SERVER1,
    BOOTSTRAP_SERVER2,
    BOOTSTRAP_SERVER3,
)

from typing import Annotated
from datetime import timedelta
from aiokafka import AIOKafkaProducer
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from app.kafka.producer_consumer import kafka_consumer, kafka_producer
from confluent_kafka.serialization import SerializationContext, MessageField
from app.protobuf import user_pb2
import asyncio


bootstrap_servers = [BOOTSTRAP_SERVER1, BOOTSTRAP_SERVER2, BOOTSTRAP_SERVER3]

auth_router = APIRouter(
    prefix="/auth", tags=["auth"], responses={404: {"description": "Not Found"}}
)

schema_registry_conf = {"url": "http://127.0.0.1:8081/"}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

protobuf_serializer = ProtobufSerializer(
    user_pb2.Users, schema_registry_client
    # , {"use.deprecated.format": False}
)


@auth_router.post("/register")
async def register_user(
    new_user: Annotated[Register_User, Depends()],
    session: Annotated[Session, Depends(get_session)],
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)],
):
    db_user = get_user_from_db(session, new_user.username, new_user.email)
    if db_user:
        raise HTTPException(
            status_code=409, detail="User with these credientials already exist"
        )
    if not db_user:
        user = user_pb2.Users(
            username=new_user.username,
            email=new_user.email,
            password=hash_password(new_user.password),
        )
        print("User: ", user)

        # ? Create the serialization context for the value
        context = SerializationContext(topic="user-register", field=MessageField.VALUE)
        print("Context: ", context)

        # ? Serialize the Protobuf message
        value = protobuf_serializer(user, context)
        print("Value: ", value)
        print("Value: ", value)

        # ? Produce the message with headers
        await producer.send_and_wait("user-register", value=value)
        # session.add(user)
        # session.commit()
        # session.refresh(user)
        return {"message": f"User with {user.username} successfully registered"}


@auth_router.post("/login", response_model=Token)
async def login_user(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    user = authenticate_user(user_data.username, user_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    expire_time = timedelta(minutes=EXPIRY_TIME)
    access_token = create_access_token({"sub": user_data.username}, expire_time)
    refresh_expire_time = timedelta(days=7)
    refresh_token = create_access_token({"sub": user.email}, refresh_expire_time)
    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


@auth_router.post("/token", response_model=Token)
def refresh_token(
    old_refresh_token: str,
    session: Annotated[Session, Depends(get_session)],
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, please login again",
        headers={"www-Authenticate": "Bearer"},
    )
    user = validate_refresh_token(old_refresh_token, session)
    if not user:
        raise credential_exception

    expire_time = timedelta(minutes=EXPIRY_TIME)
    access_token = create_access_token({"sub": user.username}, expire_time)
    refresh_expire_time = timedelta(days=7)
    refresh_token = create_access_token({"sub": user.email}, refresh_expire_time)
    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )
