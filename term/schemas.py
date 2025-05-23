from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from users.schemas import UserResponse
from odmantic import ObjectId

class Term(BaseModel):
    term_name: str
    term_start_date: datetime
    term_end_date: datetime
    term_status: bool = True
    term_created_at: datetime = datetime.utcnow()
    term_students: List[ObjectId] = []

class TermCreate(Term):
    pass

class TermUpdate(Term):
    term_name: Optional[str] = None
    term_start_date: Optional[datetime] = None
    term_end_date: Optional[datetime] = None
    term_status: Optional[bool] = None
    term_students: Optional[List[str]] = None

class Student(UserResponse):
    pass

