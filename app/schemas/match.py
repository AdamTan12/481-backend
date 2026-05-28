from pydantic import BaseModel
from datetime import datetime


class MatchResponse(BaseModel):
    id: str
    pet_a_id: str
    pet_b_id: str
    created_at: datetime
