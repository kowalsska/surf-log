import logging

from fastapi import FastAPI

from app.api.api import api_router

logging.basicConfig(level=logging.DEBUG)


PROJECT_NAME: str = "surf-api"
SURF_API_PREFIX: str = "/surf"

app = FastAPI(title=PROJECT_NAME, openapi_url=f"{SURF_API_PREFIX}/openapi.json")

app.include_router(api_router, prefix=SURF_API_PREFIX)
