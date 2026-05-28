# Database Schema

## Core Entities

### `users`
| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK · References auth.users(id) |
| `email` | text | Unique, not null |
| `first_name` | text | Not null |
| `last_name` | text | Not null |
| `password_hash` | text | Not null |
| `created_at` | timestamptz | Default now() |

---

### `pet_profiles`
| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK · gen_random_uuid() |
| `owner_id` | uuid | FK → users.id |
| `name` | text | Not null |
| `species` | text | Not null |
| `breed` | text | Optional |
| `gender` | text | Not null |
| `age` | numeric(5,2) | In years (e.g. 0.5) |
| `weight` | numeric(7,2) | Not null |
| `favorite_food` | text | Optional |
| `favorite_activity` | text | Optional |
| `personality_trait` | text | Optional |
| `bio` | text | Optional |
| `created_at` | timestamptz | Default now() |
| `updated_at` | timestamptz | Auto-updated via trigger |

---

### `images`
| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK · gen_random_uuid() |
| `url` | text | Supabase Storage URL, not null |
| `created_at` | timestamptz | Default now() |

---

### `tags`
| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK · gen_random_uuid() |
| `title` | text | Unique, not null |

---

## Likes & Matching

### `pet_likes`
One directional like per row. A match is created when both pets have liked each other.

| Column | Type | Notes |
|---|---|---|
| `liker_pet_id` | uuid | PK · FK → pet_profiles.id — the pet that liked |
| `liked_pet_id` | uuid | PK · FK → pet_profiles.id — the pet that was liked |
| `created_at` | timestamptz | Default now() |

> Composite PK on `(liker_pet_id, liked_pet_id)` prevents duplicate likes.

---

### `pet_matches`
Created when two pets have mutually liked each other. Serves as the parent for chat messages.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK · gen_random_uuid() |
| `pet_a_id` | uuid | FK → pet_profiles.id |
| `pet_b_id` | uuid | FK → pet_profiles.id |
| `created_at` | timestamptz | When the match occurred |

> `(pet_a_id, pet_b_id)` should have a unique constraint. By convention, store the lower uuid as `pet_a_id` to avoid duplicate rows for the same pair.

---

### `messages`
Chat messages scoped to a match.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK · gen_random_uuid() |
| `match_id` | uuid | FK → pet_matches.id |
| `sender_pet_id` | uuid | FK → pet_profiles.id — which pet sent the message |
| `content` | text | Not null |
| `created_at` | timestamptz | Default now() |

---

## Join Tables

### `pet_to_image`
| Column | Type | Notes |
|---|---|---|
| `pet_id` | uuid | PK · FK → pet_profiles.id |
| `image_id` | uuid | PK · FK → images.id |

> Composite PK on `(pet_id, image_id)` prevents duplicate associations.

---

### `pet_to_tag`
| Column | Type | Notes |
|---|---|---|
| `pet_id` | uuid | PK · FK → pet_profiles.id |
| `tag_id` | uuid | PK · FK → tags.id |

> Composite PK on `(pet_id, tag_id)` prevents duplicate associations.
