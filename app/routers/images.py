from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.database import get_supabase
from app.schemas.image import ImageCreate, ImageResponse
from app.routers.pets import _assert_pet_owner

router = APIRouter(prefix="/pets/{pet_id}/images", tags=["images"])


@router.get("", response_model=list[ImageResponse])
def get_pet_images(pet_id: str, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    result = (
        db.table("pet_to_image")
        .select("images(*)")
        .eq("pet_id", pet_id)
        .execute()
    )
    return [row["images"] for row in result.data]


@router.post("", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
def add_pet_image(pet_id: str, body: ImageCreate, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, pet_id, current_user["id"])
    image_result = db.table("images").insert({"url": body.url}).execute()
    image = image_result.data[0]
    db.table("pet_to_image").insert({"pet_id": pet_id, "image_id": image["id"]}).execute()
    return image


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_pet_image(pet_id: str, image_id: str, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, pet_id, current_user["id"])
    db.table("pet_to_image").delete().eq("pet_id", pet_id).eq("image_id", image_id).execute()
