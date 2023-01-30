from fastapi import APIRouter

from app.api.endpoints import surf


api_router = APIRouter()
api_router.include_router(
    surf.router,
    tags=["surf"],
)


@api_router.get("/")
def main():
    return {"Hello": "World"}
