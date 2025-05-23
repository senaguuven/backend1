from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List

class User(BaseModel):
    username: str
    user_email: str
    user_name: str
    user_surname: str
    user_fullname: Optional[str] = None
    user_role: List[str] = None
    user_status: bool = True
    user_password: str
    is_password_change_required: bool = False

class UserCreate(BaseModel):
    user_email: str
    user_name: str
    user_surname: str
    user_role: List[str] = None
    user_status: bool = True
    user_password: str
    is_password_change_required: bool = False


class UserResponse(BaseModel):
    username: str
    user_email: str
    user_name: str
    user_surname: str
    user_fullname: Optional[str] = None
    user_role: List[str] = None
    user_status: bool = True
    is_passwrord_change_required: bool = False
    

class Token(BaseModel):
    access_token: str
    token_type: str
    user_data: User

class TokenData(BaseModel):
    username: str
    user_role: List[str] = None
