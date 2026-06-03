import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.dependencies import get_current_user
from app.database import get_supabase, get_admin_client
from app.schemas.image import ImageResponse
from app.routers.pets import _assert_pet_owner
from app.config import settings

STORAGE_BUCKET = "pet-images"

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
async def add_pet_image(
    pet_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, pet_id, current_user["id"])

    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    storage_path = f"{pet_id}/{uuid.uuid4()}.{ext}"
    contents = await file.read()

    admin = get_admin_client()
    admin.storage.from_(STORAGE_BUCKET).upload(
        path=storage_path,
        file=contents,
        file_options={"content-type": file.content_type or "application/octet-stream"},
    )

    public_url = f"{settings.supabase_url}/storage/v1/object/public/{STORAGE_BUCKET}/{storage_path}"

    image_result = db.table("images").insert({"url": public_url}).execute()
    image = image_result.data[0]
    db.table("pet_to_image").insert({"pet_id": pet_id, "image_id": image["id"]}).execute()
    return image


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_pet_image(pet_id: str, image_id: str, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, pet_id, current_user["id"])
    db.table("pet_to_image").delete().eq("pet_id", pet_id).eq("image_id", image_id).execute()
    db.table("images").delete().eq("id", image_id).execute()
