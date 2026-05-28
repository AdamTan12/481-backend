from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.database import get_supabase, get_admin_client
from app.schemas.like import LikeResponse
from app.schemas.match import MatchResponse
from app.routers.pets import _assert_pet_owner

router = APIRouter(tags=["likes"])


@router.post(
    "/pets/{liker_pet_id}/like/{liked_pet_id}",
    status_code=status.HTTP_201_CREATED,
)
def like_pet(
    liker_pet_id: str,
    liked_pet_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, liker_pet_id, current_user["id"])

    db.table("pet_likes").insert(
        {"liker_pet_id": liker_pet_id, "liked_pet_id": liked_pet_id}
    ).execute()

    # Check for a mutual like → create match if one doesn't exist yet
    mutual = (
        db.table("pet_likes")
        .select("*")
        .eq("liker_pet_id", liked_pet_id)
        .eq("liked_pet_id", liker_pet_id)
        .execute()
    )

    if mutual.data:
        pet_a, pet_b = sorted([liker_pet_id, liked_pet_id])
        admin = get_admin_client()
        existing = (
            admin.table("pet_matches")
            .select("id")
            .eq("pet_a_id", pet_a)
            .eq("pet_b_id", pet_b)
            .execute()
        )
        if not existing.data:
            match_result = (
                admin.table("pet_matches")
                .insert({"pet_a_id": pet_a, "pet_b_id": pet_b})
                .execute()
            )
            return {"liked": True, "matched": True, "match": match_result.data[0]}

    return {"liked": True, "matched": False}


@router.delete("/pets/{liker_pet_id}/like/{liked_pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlike_pet(
    liker_pet_id: str,
    liked_pet_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_supabase(current_user["token"])
    _assert_pet_owner(db, liker_pet_id, current_user["id"])
    db.table("pet_likes").delete().eq("liker_pet_id", liker_pet_id).eq("liked_pet_id", liked_pet_id).execute()
