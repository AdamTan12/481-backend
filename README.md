# 481 Pet Matching API

A REST API for a pet-matching app built with FastAPI and Supabase.

**Base URL (production):** `https://your-railway-url.up.railway.app`  
**Interactive docs:** `{base_url}/docs`

---

## Authentication

Every endpoint (except `/health`) requires a **Supabase JWT** in the `Authorization` header.

Your frontend handles login/signup via Supabase Auth. Once the user is signed in, pass the session's `access_token`:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Health

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Check that the server is running |

---

### Auth

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create a new account |
| POST | `/auth/login` | Sign in and get tokens |
| POST | `/auth/logout` | Invalidate the current session |

**POST `/auth/register` body:**
```json
{
  "email": "ada@example.com",
  "password": "supersecret",
  "first_name": "Ada",
  "last_name": "Lovelace"
}
```
> No `Authorization` header needed. Returns the created user profile.

**POST `/auth/login` body:**
```json
{
  "email": "ada@example.com",
  "password": "supersecret"
}
```
> No `Authorization` header needed. Returns tokens to use for all subsequent requests.

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**POST `/auth/logout`**
> Requires `Authorization` header. Invalidates the session on Supabase's side. Returns `204 No Content`.

---

### Users

| Method | Path | Description |
|---|---|---|
| GET | `/users/me` | Get your own profile |
| PATCH | `/users/me` | Update your profile |

**PATCH `/users/me` body:**
```json
{
  "first_name": "Ada",
  "last_name": "Lovelace"
}
```

---

### Pet Profiles

| Method | Path | Description |
|---|---|---|
| GET | `/pets/discover` | Browse pets for swiping (excludes your own) |
| GET | `/pets/mine` | List all your pets |
| POST | `/pets` | Create a new pet profile |
| GET | `/pets/{pet_id}` | Get a pet by ID |
| PATCH | `/pets/{pet_id}` | Update a pet (must be owner) |
| DELETE | `/pets/{pet_id}` | Delete a pet (must be owner) |

**GET `/pets/discover` query params:**
| Param | Type | Description |
|---|---|---|
| `species` | string | Filter by species (e.g. `dog`, `cat`) |
| `limit` | int | Max results, default `20`, max `100` |

**POST `/pets` body:**
```json
{
  "name": "Biscuit",
  "species": "dog",
  "breed": "Golden Retriever",
  "gender": "male",
  "age": 2.5,
  "weight": 30.0,
  "favorite_food": "peanut butter",
  "favorite_activity": "fetch",
  "personality_trait": "playful",
  "bio": "Loves everyone he meets."
}
```
> `name`, `species`, `gender`, `weight` are required. All others are optional.

---

### Images

Images are stored in Supabase Storage — upload the file from your frontend to get a URL, then register that URL here.

| Method | Path | Description |
|---|---|---|
| GET | `/pets/{pet_id}/images` | List all images for a pet |
| POST | `/pets/{pet_id}/images` | Add an image to a pet (must be owner) |
| DELETE | `/pets/{pet_id}/images/{image_id}` | Remove an image from a pet (must be owner) |

**POST `/pets/{pet_id}/images` body:**
```json
{
  "url": "https://your-project.supabase.co/storage/v1/object/public/pets/biscuit.jpg"
}
```

---

### Tags

Tags are labels you attach to pets (e.g. `vaccinated`, `friendly`, `indoor`).

| Method | Path | Description |
|---|---|---|
| GET | `/tags` | List all available tags |
| GET | `/pets/{pet_id}/tags` | Get tags for a pet |
| POST | `/pets/{pet_id}/tags` | Add a tag to a pet (must be owner) |
| DELETE | `/pets/{pet_id}/tags/{tag_id}` | Remove a tag from a pet (must be owner) |

**POST `/pets/{pet_id}/tags` body:**
```json
{
  "title": "vaccinated"
}
```
> Tags are created automatically if they don't exist yet.

---

### Likes

| Method | Path | Description |
|---|---|---|
| POST | `/pets/{liker_pet_id}/like/{liked_pet_id}` | Like another pet (must own the liker pet) |
| DELETE | `/pets/{liker_pet_id}/like/{liked_pet_id}` | Undo a like |

**POST like — response:**
```json
{ "liked": true, "matched": false }
```
If both pets have liked each other, a match is created automatically:
```json
{
  "liked": true,
  "matched": true,
  "match": {
    "id": "uuid",
    "pet_a_id": "uuid",
    "pet_b_id": "uuid",
    "created_at": "2026-05-27T00:00:00Z"
  }
}
```

---

### Matches

| Method | Path | Description |
|---|---|---|
| GET | `/matches/pets/{pet_id}` | List all matches for a pet |
| GET | `/matches/{match_id}` | Get a specific match |

---

### Messages

Messages are scoped to a match. Both pet owners in a match can read and send.

| Method | Path | Description |
|---|---|---|
| GET | `/matches/{match_id}/messages` | Get messages in a match |
| POST | `/matches/{match_id}/messages` | Send a message |

**GET messages query params:**
| Param | Type | Description |
|---|---|---|
| `limit` | int | Max results, default `50`, max `200` |

**POST `/matches/{match_id}/messages` body:**
```json
{
  "sender_pet_id": "uuid-of-your-pet",
  "content": "Hey! Biscuit wants to play!"
}
```

---

## Running Locally

1. **Clone and install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Fill in your Supabase credentials in .env
   ```

   | Variable | Where to find it |
   |---|---|
   | `SUPABASE_URL` | Supabase dashboard → Project Settings → API |
   | `SUPABASE_ANON_KEY` | Supabase dashboard → Project Settings → API |
   | `SUPABASE_SERVICE_ROLE_KEY` | Supabase dashboard → Project Settings → API |
   | `SUPABASE_JWT_SECRET` | Supabase dashboard → Project Settings → API → JWT Secret |

3. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```
   API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## Error Responses

All errors follow this shape:

```json
{ "detail": "Human-readable error message" }
```

| Status | Meaning |
|---|---|
| 400 | Bad request (e.g. no fields to update) |
| 401 | Missing or invalid JWT |
| 403 | Authenticated but not authorized (e.g. not the pet owner) |
| 404 | Resource not found |
