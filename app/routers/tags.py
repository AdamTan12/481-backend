from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.database import get_supabase
from app.schemas.tag import TagCreate, TagResponse
from app.routers.pets import _assert_pet_owner

router = APIRouter(tags=["tags"])


@router.get("/tags", response_model=list[TagResponse])
def list_tags(current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    result = db.table("tags").select("*").order("title").execute()
    return result.data


@router.get("/pets/{pet_id}/tags", response_model=list[TagResponse])
def get_pet_tags(pet_id: str, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    result = db.table("pet_to_tag").select("tags(*)").eq("pet_id", pet_id).execute()
    return [row["tags"] for row in result.data]


@router.post("/pets/{pet_id}/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def add_tag_to_pet(pet_id: str, body: TagCreate, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, pet_id, current_user["id"])
    tag_result = db.table("tags").upsert({"title": body.title}, on_conflict="title").execute()
    tag = tag_result.data[0]
    db.table("pet_to_tag").upsert({"pet_id": pet_id, "tag_id": tag["id"]}).execute()
    return tag


@router.delete("/pets/{pet_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_pet(pet_id: str, tag_id: str, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, pet_id, current_user["id"])
    db.table("pet_to_tag").delete().eq("pet_id", pet_id).eq("tag_id", tag_id).execute()
