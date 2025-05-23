from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

from . import schemas as user_schemas, crud as user_crud
from config import auth

from config.database import db

from typing import List

controller = APIRouter()

@controller.on_event("startup")
async def create_default_admin():
    admin = await user_crud.get_user("umut.firat")
    if not admin:
        default_admin = {
            "user_password": auth.get_password_hash("827ccb0eea8a706c4c34a16891f84e7b"),
            "user_email": "umut.firat@samsun.edu.tr",
            "user_role": ["admin", "user", "student"],
            "user_name": "Kutsal Umut",
            "user_surname": "Fırat",
            "user_status": True,
        }
        await user_crud.create_user(default_admin)
    await user_crud.__migrate__()

#Authentication

@controller.post("/login", response_model=user_schemas.Token)
async def login(user_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_crud.check_login(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_data": user}

@controller.post("/", response_model=user_schemas.UserResponse)
async def create_user(user_data: user_schemas.UserCreate, current_user: user_schemas.User = Depends(auth.check_user(["admin"]))):
    user = await user_crud.get_user(user_data.user_email.split("@")[0])
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered"
        )
    user_data.user_password = auth.get_password_hash(user_data.user_password)
    user = await user_crud.create_user(user_data.dict())
    return user

@controller.get("/", response_model=List[user_schemas.UserResponse])
async def get_users(current_user: user_schemas.User = Depends(auth.check_user(["admin", "user"]))):
    users = await user_crud.list_users()
    return users