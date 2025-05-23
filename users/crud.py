from config.database import db
from odmantic import ObjectId
from typing import List
from config import auth

from users.model import User

async def __migrate__():
    db.client.kankanX.users.create_index([("username", 1)], unique=True)
    db.client.kankanX.users.create_index([("user_email", 1)], unique=True)

async def get_user(username: str) -> User | None:
    return await db.find_one(User, User.username == username)

async def check_login(username: str, password: str) -> User | bool:
    user = await db.find_one(User, User.username == username)
    return user if auth.verify_password(password, user.user_password) else False

async def create_user(user_data: dict) -> User:
    user_data["username"] = user_data["user_email"].split("@")[0]
    user = User(**user_data)
    await db.save(user)
    return user

async def list_users() -> List[User]:
    return await db.find(User)

async def delete_user(user_id: ObjectId) -> bool:
    user = await db.find_one(User, User.id == user_id)
    if not user:
        return False
    await db.delete(user)
    return True

async def update_user(username: str, user_data: dict) -> User | bool:
    user = await db.find_one(User, User.username == username)
    if not user:
        return False
    for key, value in user_data.items():
        setattr(user, key, value)
    await db.save(user)
    return user

async def get_user_by_id(user_id: ObjectId) -> User | None:
    return await db.find_one(User, User.id == user_id)