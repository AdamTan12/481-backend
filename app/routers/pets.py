from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.dependencies import get_current_user
from app.database import get_supabase
from app.schemas.pet import PetCreate, PetUpdate, PetResponse

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("/discover", response_model=list[PetResponse])
def discover_pets(
    species: str | None = Query(None),
    limit: int = Query(20, le=100),
    current_user: dict = Depends(get_current_user),
):
    """Return pets not owned by the current user for the swiping feed."""
    db = get_supabase(current_user["token"])
    query = (
        db.table("pet_profiles")
        .select("*")
        .neq("owner_id", current_user["id"])
        .limit(limit)
    )
    if species:
        query = query.eq("species", species)
    result = query.execute()
    return result.data


@router.get("/mine", response_model=list[PetResponse])
def get_my_pets(current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    result = db.table("pet_profiles").select("*").eq("owner_id", current_user["id"]).execute()
    return result.data


@router.post("", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(body: PetCreate, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    payload = body.model_dump(exclude_none=True)
    payload["owner_id"] = current_user["id"]
    result = db.table("pet_profiles").insert(payload).execute()
    return result.data[0]


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    result = db.table("pet_profiles").select("*").eq("id", pet_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
    return result.data


@router.patch("/{pet_id}", response_model=PetResponse)
def update_pet(pet_id: str, body: PetUpdate, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, pet_id, current_user["id"])
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    result = db.table("pet_profiles").update(updates).eq("id", pet_id).execute()
    return result.data[0]


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: str, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, pet_id, current_user["id"])
    db.table("pet_profiles").delete().eq("id", pet_id).execute()


def _assert_pet_owner(db, pet_id: str, user_id: str):
    result = db.table("pet_profiles").select("owner_id").eq("id", pet_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
    if result.data["owner_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your pet")
