from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.database import get_supabase
from app.schemas.match import MatchResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/pets/{pet_id}", response_model=list[MatchResponse])
def get_pet_matches(pet_id: str, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    result = (
        db.table("pet_matches")
        .select("*")
        .or_(f"pet_a_id.eq.{pet_id},pet_b_id.eq.{pet_id}")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: str, current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    result = db.table("pet_matches").select("*").eq("id", match_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return result.data
