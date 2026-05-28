from pydantic import BaseModel
from datetime import datetime


class MessageCreate(BaseModel):
    content: str
    sender_pet_id: str


class MessageResponse(BaseModel):
    id: str
    match_id: str
    sender_pet_id: str
    content: str
    created_at: datetime
