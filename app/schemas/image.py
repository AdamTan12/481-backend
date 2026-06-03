from pydantic import BaseModel
from datetime import datetime



class ImageResponse(BaseModel):
    id: str
    url: str
    created_at: datetime
