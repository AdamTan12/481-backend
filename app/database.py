from supabase import create_client, Client
from app.config import settings

# Client for user-level operations (respects RLS)
def get_supabase(access_token: str | None = None) -> Client:
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    if access_token:
        client.postgrest.auth(access_token)
    return client


# Admin client that bypasses RLS — use only for server-side logic
def get_admin_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
