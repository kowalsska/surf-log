import os

from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

workdir = os.getcwd()
load_dotenv(f"{workdir}/vars.env")

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

MAIN_API_KEY = os.environ.get("MAIN_API_KEY")


def verify_api_key(api_key_header: str = Security(api_key_header)) -> str:
    is_correct = api_key_header == MAIN_API_KEY
    if not is_correct:
        raise HTTPException(status_code=400, detail="API Key incorrect")
    return "verified"
