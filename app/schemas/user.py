from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    created_at: datetime


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
