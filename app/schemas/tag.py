from pydantic import BaseModel


class TagResponse(BaseModel):
    id: str
    title: str


class TagCreate(BaseModel):
    title: str
