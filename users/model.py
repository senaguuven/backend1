from odmantic import Model
from datetime import datetime
from pydantic import field_validator, EmailStr
from typing import Optional

class User(Model):
    username: str
    user_email: str
    user_name: str
    user_surname: str
    user_role: Optional[list[str]] = None
    user_status: bool
    user_password: str
    is_password_change_required: bool
    user_created_at: datetime = datetime.utcnow()

    @property
    def user_fullname(self) -> str:
        return f"{self.user_name} {self.user_surname}"
        
    @field_validator("user_email", mode="before")
    def validate_user_email(cls, value: str) -> str:
        if not value.endswith("@samsun.edu.tr"):
            raise ValueError("samsun.edu.tr e-posta adresini kullanmalısınız.")
        
        return value.lower()
    
    model_config = {
        "collection": "users",
        "indexes": ["username", "user_email"]
    }