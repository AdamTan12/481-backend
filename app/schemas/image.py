from pydantic import BaseModel
from datetime import datetime


class ImageCreate(BaseModel):
    url: str


class ImageResponse(BaseModel):
    id: str
    url: str
    created_at: datetime
