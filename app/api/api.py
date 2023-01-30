from fastapi import APIRouter

from app.api.endpoints import surf

SURF_API_PREFIX: str = "/surf"

api_router = APIRouter()
api_router.include_router(
    surf.router,
    tags=["surf"],
    prefix=SURF_API_PREFIX
)

## HELLO WORLD

@api_router.get("/")
def main():
    return {"Hello": "World"}
