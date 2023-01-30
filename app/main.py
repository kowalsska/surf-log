import logging

from fastapi import FastAPI

from app.api.api import api_router

logging.basicConfig(level=logging.DEBUG)


PROJECT_NAME: str = "surf-api"

app = FastAPI(title=PROJECT_NAME, openapi_url=f"/openapi.json")

app.include_router(api_router)
