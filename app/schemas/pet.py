from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class PetCreate(BaseModel):
    name: str
    species: str
    breed: str | None = None
    gender: str
    age: Decimal | None = None
    weight: Decimal
    favorite_food: str | None = None
    favorite_activity: str | None = None
    personality_trait: str | None = None
    bio: str | None = None


class PetUpdate(BaseModel):
    name: str | None = None
    species: str | None = None
    breed: str | None = None
    gender: str | None = None
    age: Decimal | None = None
    weight: Decimal | None = None
    favorite_food: str | None = None
    favorite_activity: str | None = None
    personality_trait: str | None = None
    bio: str | None = None


class PetResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    species: str
    breed: str | None
    gender: str
    age: Decimal | None
    weight: Decimal
    favorite_food: str | None
    favorite_activity: str | None
    personality_trait: str | None
    bio: str | None
    created_at: datetime
    updated_at: datetime | None
