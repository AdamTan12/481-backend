from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_admin_client, get_supabase
from app.dependencies import get_current_user
from app.schemas.auth import RegisterRequest, LoginRequest, LoginResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    admin = get_admin_client()

    # Create the auth user — this generates the UUID we'll reuse
    auth_response = admin.auth.admin.create_user({
        "email": body.email,
        "password": body.password,
        "email_confirm": True,
    })

    if not auth_response.user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create auth user")

    user_id = auth_response.user.id

    # Insert into public.users with the same ID
    result = admin.table("users").insert({
        "id": user_id,
        "email": body.email,
        "first_name": body.first_name,
        "last_name": body.last_name,
        "password_hash": "",  # auth is handled by Supabase, not stored here
    }).execute()

    if not result.data:
        # Roll back the auth user if the DB insert failed
        admin.auth.admin.delete_user(user_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user profile")

    return result.data[0]


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    db = get_supabase()
    response = db.auth.sign_in_with_password({"email": body.email, "password": body.password})

    if not response.session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return LoginResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: dict = Depends(get_current_user)):
    db = get_supabase(current_user["token"])
    db.auth.sign_out()

