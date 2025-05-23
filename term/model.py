from odmantic import Model, Reference, ObjectId
from datetime import datetime, timezone
from pydantic import model_validator
from typing import Optional, List
from users.model import User

class Term(Model):
    term_name: str
    term_start_date: datetime
    term_end_date: datetime
    term_status: bool = True
    term_created_at: datetime = datetime.now(timezone.utc)
    term_students: List[ObjectId]

    @property
    def term_duration(self) -> str:
        return f"{self.term_start_date.strftime('%d-%m-%Y')} - {self.term_end_date.strftime('%d-%m-%Y')}"
    
    @property
    def term_year(self) -> int:
        return self.term_start_date.year

    @model_validator(mode="after")
    def check_dates(self) -> 'Term':
        if self.term_end_date < datetime.now():
            raise ValueError("Term end date cannot be in the past.")
        if self.term_end_date < self.term_start_date:
            raise ValueError("Term end date cannot be earlier than start date.")
        return self
    
    model_config = {
        "collection": "terms",
        "indexes": ["term_name", "term_year"]
    }