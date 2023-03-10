import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import verify_api_key
from app.core.helpers import get_buoy_reading, get_region_conditions, get_wind_data
from app.core.surfline import get_access_token
from app.models import LatestBuoyData, WindData

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/rat")
def refresh_access_token(verified: str = Depends(verify_api_key)):
    resp = get_access_token()
    return "<3" if resp == 1 else "</3"


@router.get("/conditions")
def get_conditions(
    spot: str, days: int, now: bool = False, verified: str = Depends(verify_api_key)
):
    logger.info(f"New GET /conditions {spot} {days} now={now}!")
    cond_data = get_region_conditions(spot, days, now)
    if not cond_data:
        raise HTTPException(
            status_code=500, detail=f"Could not load conditions for {spot}."
        )
    return cond_data


@router.get("/buoy", response_model=LatestBuoyData)
def get_current_buoy_reading(spot: str, verified: str = Depends(verify_api_key)):
    logger.info(f"New GET /buoy request for {spot}")
    buoy_data = get_buoy_reading(spot)
    if not buoy_data:
        raise HTTPException(
            status_code=500, detail=f"Data for buoy at {spot} not found"
        )
    return buoy_data


@router.get("/wind", response_model=WindData)
def get_wind(spot: str, days: int, verified: str = Depends(verify_api_key)):
    logger.info(f"New GET /wind request for {spot}")
    if days > 1:
        raise HTTPException(
            status_code=501, detail=f"Could not load wind data for days > 1."
        )
    wind_data = get_wind_data(spot, days)
    if not wind_data:
        raise HTTPException(
            status_code=500, detail=f"Could not load wind data for spot {spot}."
        )
    return wind_data
