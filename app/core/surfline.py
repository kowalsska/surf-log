import logging
import os
from http import HTTPStatus
from typing import Optional, Tuple

import requests
from dotenv import load_dotenv

from app.db.locations import REGIONS, SPOTS
from app.models import (ConditionsResponse, NearbyResponse, RatingResponse,
                        TideResponse, WaveResponse, WindResponse)

logger = logging.getLogger(__name__)

workdir = os.getcwd()
load_dotenv(f"{workdir}/vars.env")

USERNAME = os.environ.get("SURFLINE_USERNAME")
PASSWORD = os.environ.get("SURFLINE_PASSWORD")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
AUTH_STRING = os.environ.get("AUTH_STRING")

BASE_URL = os.environ.get("SURFLINE_BASE_URL")
LOGIN_PATH = os.environ.get("LOGIN_PATH")
CONDITIONS_PATH = os.environ.get("CONDITIONS_PATH")
WAVE_PATH = os.environ.get("WAVE_PATH")
RATING_PATH = os.environ.get("RATING_PATH")
WIND_PATH = os.environ.get("WIND_PATH")
TIDES_PATH = os.environ.get("TIDES_PATH")
NEARBY_PATH = os.environ.get("NEARBY_PATH")


def get_access_token() -> int:
    body = {
        "authorizationString": AUTH_STRING,
        "device_id": "Chrome-109.0.0.0",
        "device_type": "Chrome 109.0.0.0 on OS X 10.15.7 64-bit",
        "forced": True,
        "grant_type": "password",
        "password": PASSWORD,
        "username": USERNAME,
    }
    params = {"isShortLived": False}
    url = f"{BASE_URL}{LOGIN_PATH}"
    resp = requests.post(url, params=params, json=body)
    if resp.status_code != 200:
        print(f"{resp} {resp.text}")
        return -1

    r_json = resp.json()
    logger.info(f"New access token: {r_json['access_token']}")
    return 1


def get_conditions(
    region: str = "oahu_north_shore", days: int = 8
) -> Tuple[HTTPStatus, Optional[ConditionsResponse]]:
    params = {
        "subregionId": REGIONS[region]["region_id"],
        "days": days,
        "accesstoken,omitempty": ACCESS_TOKEN,
    }
    url = f"{BASE_URL}{CONDITIONS_PATH}"
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return _handle_failure(resp)

    r_json = resp.json()
    r_json["region"] = region
    return _parse_response(r_json, ConditionsResponse)


def get_wave(
    spot: str, days: int = 3, interval_hours: int = 8, max_heights: bool = False
) -> Tuple[HTTPStatus, Optional[WaveResponse]]:
    spot_data = SPOTS.get(spot)
    params = {
        "spotId": spot_data.get("spot_id"),
        "days": days,
        "intervalHours": interval_hours,
        "maxHeights": max_heights,
        "accesstoken,omitempty": ACCESS_TOKEN,
    }
    url = f"{BASE_URL}{WAVE_PATH}"
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return _handle_failure(resp)

    r_json = resp.json()
    r_json["spot"] = spot_data.get("name")
    return _parse_response(r_json, WaveResponse)


def get_rating(
    spot: str, days: int = 3, interval_hours: int = 8
) -> Tuple[HTTPStatus, Optional[RatingResponse]]:
    spot_data = SPOTS.get(spot)
    params = {
        "spotId": spot_data.get("spot_id"),
        "days": days,
        "intervalHours": interval_hours,
        "accesstoken,omitempty": ACCESS_TOKEN,
    }
    url = f"{BASE_URL}{RATING_PATH}"
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return _handle_failure(resp)

    r_json = resp.json()
    r_json["spot"] = spot_data.get("name")
    return _parse_response(r_json, RatingResponse)


def get_wind(
    spot: str, days: int = 3, interval_hours: int = 8
) -> Tuple[HTTPStatus, Optional[WindResponse]]:
    spot_data = SPOTS.get(spot)
    params = {
        "spotId": spot_data.get("spot_id"),
        "days": days,
        "intervalHours": interval_hours,
        "corrected": True,
        "accesstoken,omitempty": ACCESS_TOKEN,
    }
    url = f"{BASE_URL}{WIND_PATH}"
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return _handle_failure(resp)

    r_json = resp.json()
    r_json["spot"] = spot_data.get("name")
    return _parse_response(r_json, WindResponse)


def get_tide(spot: str, days: int = 3) -> Tuple[HTTPStatus, Optional[TideResponse]]:
    spot_data = SPOTS.get(spot)
    params = {
        "spotId": spot_data.get("spot_id"),
        "days": days,
        "accesstoken,omitempty": ACCESS_TOKEN,
    }
    url = f"{BASE_URL}{TIDES_PATH}"
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return _handle_failure(resp)

    r_json = resp.json()
    r_json["spot"] = spot_data.get("name")
    return _parse_response(r_json, TideResponse)


def get_nearby(lat: float, long: float) -> Tuple[HTTPStatus, Optional[NearbyResponse]]:
    params = {
        "latitude": lat,
        "longitude": long,
        "accesstoken,omitempty": ACCESS_TOKEN,
    }
    url = f"{BASE_URL}{NEARBY_PATH}"
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        logger.error("Failed GET %s", url)
        return _handle_failure(resp)

    r_json = resp.json()
    return _parse_response(r_json, NearbyResponse)


def _handle_failure(resp):
    logger.error(resp)
    logger.error(resp.json())
    return HTTPStatus(resp.status_code), None


def _parse_response(resp_json, resp_model):
    r_data = None
    try:
        r_data = resp_model.parse_obj(resp_json)
    except Exception as e:
        logger.error(str(e))
        return HTTPStatus.INTERNAL_SERVER_ERROR, r_data
    else:
        return HTTPStatus.OK, r_data
