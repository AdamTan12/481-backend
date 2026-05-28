from pydantic import BaseModel
from datetime import datetime


class LikeResponse(BaseModel):
    liker_pet_id: str
    liked_pet_id: str
    created_at: datetime
