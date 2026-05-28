from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.dependencies import get_current_user
from app.database import get_supabase
from app.schemas.message import MessageCreate, MessageResponse
from app.routers.pets import _assert_pet_owner

router = APIRouter(prefix="/matches/{match_id}/messages", tags=["messages"])


def _assert_match_participant(db, match_id: str, user_id: str):
    match = db.table("pet_matches").select("pet_a_id,pet_b_id").eq("id", match_id).single().execute()
    if not match.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    pets = db.table("pet_profiles").select("id").eq("owner_id", user_id).execute()
    pet_ids = {p["id"] for p in pets.data}
    if not (match.data["pet_a_id"] in pet_ids or match.data["pet_b_id"] in pet_ids):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a participant of this match")


@router.get("", response_model=list[MessageResponse])
def get_messages(
    match_id: str,
    limit: int = Query(50, le=200),
    current_user: dict = Depends(get_current_user),
):
    db = get_supabase(current_user["token"])
    _assert_match_participant(db, match_id, current_user["id"])
    result = (
        db.table("messages")
        .select("*")
        .eq("match_id", match_id)
        .order("created_at")
        .limit(limit)
        .execute()
    )
    return result.data


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    match_id: str,
    body: MessageCreate,
    current_user: dict = Depends(get_current_user),
):
    db = get_supabase(current_user["token"])
    _assert_match_participant(db, match_id, current_user["id"])
    _assert_pet_owner(db, body.sender_pet_id, current_user["id"])
    result = db.table("messages").insert(
        {
            "match_id": match_id,
            "sender_pet_id": body.sender_pet_id,
            "content": body.content,
        }
    ).execute()
    return result.data[0]
