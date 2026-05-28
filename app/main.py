from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, pets, images, tags, likes, matches, messages

app = FastAPI(title="481 Pet Matching API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(pets.router)
app.include_router(images.router)
app.include_router(tags.router)
app.include_router(likes.router)
app.include_router(matches.router)
app.include_router(messages.router)


@app.get("/health")
def health():
    return {"status": "ok"}
