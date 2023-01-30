import logging
from datetime import datetime
from http import HTTPStatus
from typing import List, Optional
from zoneinfo import ZoneInfo

from app.core.surfline import (get_conditions, get_nearby, get_rating,
                               get_tide, get_wave, get_wind)
from app.db.locations import REGIONS, SPOTS
from app.models import (LatestBuoyData, RatingInterval, RegionalReport,
                        RegionInfo, TideInterval, WaveInterval, WindInterval)

logger = logging.getLogger(__name__)

SPOT = "pipeline"
DAYS = 3
INTERVAL_HOURS = 4


def print_conditions(region="oahu_south_shore", days=10):
    status, data = get_conditions(region=region, days=days)
    if status != HTTPStatus.OK:
        print(f"Error when getting data for `{region}`")

    print(f"Data for region: {data.region}")
    for day in data.data.conditions:
        dt_object = datetime.fromtimestamp(day.timestamp)
        print(f"{dt_object.strftime('%m/%d/%Y')}")
        print(f"AM: {day.am.rating}; {day.am.humanRelation}; {day.am.observation}")
        print(f"PM: {day.pm.rating}; {day.pm.humanRelation}; {day.pm.observation}")


def print_wave(spot=SPOT, days=DAYS, interval_hours=INTERVAL_HOURS):
    status, data = get_wave(spot=spot, days=days, interval_hours=interval_hours)
    if status != HTTPStatus.OK:
        print(f"Error when getting wave data for `{spot}`")

    print(f"Data for spot: {data.spot}")
    for interval in data.data.wave:
        dt_object = datetime.fromtimestamp(interval.timestamp)
        print(f"{dt_object.strftime('%m/%d/%Y %H:%M:%S')}")
        print(f"{interval.surf}")
        for swell in interval.swells:
            print(f"{swell}")


def print_rating(spot=SPOT, days=DAYS, interval_hours=INTERVAL_HOURS):
    status, data = get_rating(spot=spot, days=days, interval_hours=interval_hours)
    if status != HTTPStatus.OK:
        print(f"Error when getting wave data for `{spot}`")

    print(f"Data for spot: {data.spot}")
    for interval in data.data.rating:
        dt_object = datetime.fromtimestamp(interval.timestamp)
        print(f"{dt_object.strftime('%m/%d/%Y %H:%M:%S')}")
        print(interval.rating)


def print_wind(spot=SPOT, days=DAYS, interval_hours=INTERVAL_HOURS):
    status, data = get_wind(spot=spot, days=days, interval_hours=interval_hours)
    if status != HTTPStatus.OK:
        print(f"Error when getting wave data for `{spot}`")

    print(f"Data for spot: {data.spot}")
    for interval in data.data.wind:
        dt_object = datetime.fromtimestamp(interval.timestamp)
        print(f"{dt_object.strftime('%m/%d/%Y %H:%M:%S')}")
        print(interval.speed, interval.direction, interval.directionType)


def print_tide(spot=SPOT, days=DAYS):
    status, data = get_tide(spot=spot, days=days)
    if status != HTTPStatus.OK:
        print(f"Error when getting wave data for `{spot}`")

    print(f"Data for spot: {data.spot}")
    for interval in data.data.tides:
        dt_object = datetime.fromtimestamp(interval.timestamp)
        print(f"{dt_object.strftime('%m/%d/%Y %H:%M:%S')}")
        print(interval.height, interval.type)


def get_wave_data_intervals(intervals: List[WaveInterval]) -> dict:
    out = {}
    for i in intervals:
        dt_object = datetime.fromtimestamp(i.timestamp)
        dt_key = dt_object.strftime("%m/%d/%Y %H:%M:%S")
        out[dt_key] = {
            "surf": i.surf,
            "swells": i.swells,
        }
    return out


def get_wind_data_intervals(intervals: List[WindInterval]) -> dict:
    out = {}
    for i in intervals:
        dt_object = datetime.fromtimestamp(i.timestamp)
        dt_key = dt_object.strftime("%m/%d/%Y %H:%M:%S")
        out[dt_key] = {
            "speed": i.speed,
            "direction": i.direction,
            "direction_type": i.directionType,
            "optimal_score": i.optimalScore,
        }
    return out


def get_rating_data_intervals(intervals: List[RatingInterval]) -> dict:
    out = {}
    for i in intervals:
        dt_object = datetime.fromtimestamp(i.timestamp)
        dt_key = dt_object.strftime("%m/%d/%Y %H:%M:%S")
        out[dt_key] = {
            "rating": i.rating,
        }
    return out


def get_full_report(spot, days):
    status, wave_data = get_wave(spot, days, interval_hours=3)
    status, wind_data = get_wind(spot, days, interval_hours=3)
    # status, rating_data = get_rating(spot, days, interval_hours=3)
    # status, tide_data = get_tide(spot, days)
    wave_intervals = get_wave_data_intervals(wave_data.data.wave)
    wind_intervals = get_wind_data_intervals(wind_data.data.wind)
    # rating_intervals = get_rating_data_intervals(rating_data.data.rating)
    # wave_intervals.update(rating_intervals)
    return wave_intervals, wave_data.associated.units


def get_region_info(spot: str) -> Optional[RegionInfo]:
    spot_data = SPOTS.get(spot)
    if not spot_data:
        return None

    region = spot_data["region"]
    region_data = REGIONS.get(region)
    if not region_data:
        return None

    region_data["region_name"] = region
    return RegionInfo.parse_obj(region_data)


def get_local_buoy_datetime(timestamp: int, timezone: str) -> datetime:
    utc = ZoneInfo("UTC")
    utc_dt = datetime.fromtimestamp(timestamp).replace(tzinfo=utc)
    local_tz = ZoneInfo(timezone)
    return utc_dt.astimezone(local_tz)


def get_buoy_reading(spot: str) -> Optional[LatestBuoyData]:
    reg_info = get_region_info(spot)
    if not reg_info:
        logger.warning("Did not find region info for %s", spot)
        return None

    status, nearby_data = get_nearby(reg_info.latitude, reg_info.longitude)
    if status != HTTPStatus.OK:
        return None

    spot_buoy = next((b for b in nearby_data.data if b.id == reg_info.buoy_id), None)
    if spot_buoy.status != "ONLINE":
        logger.warning("Buoy %s is not online", spot_buoy.id)

    local_buoy_datetime = get_local_buoy_datetime(
        spot_buoy.latestData.timestamp, spot_buoy.abbrTimezone
    )
    data = {
        "name": spot_buoy.name,
        "source_id": spot_buoy.sourceId,
        "buoy_local_datetime": local_buoy_datetime,
        "wave_height": spot_buoy.latestData.height,
        "wave_period": spot_buoy.latestData.period,
        "swells": spot_buoy.latestData.swells,
    }
    return LatestBuoyData.parse_obj(data)

def get_region_conditions(spot: str, days:int, now: bool) -> Optional[RegionalReport]:
    reg_info = get_region_info(spot)
    if not reg_info:
        logger.warning("Did not find region info for %s", spot)
        return None
    
    status, cond = get_conditions(reg_info.region_name, days)
    if status != HTTPStatus.OK:
        return None
    
    day_cond = cond.data.conditions[0]
    reg_dttm = get_local_buoy_datetime(day_cond.timestamp, reg_info.timezone)
    am_cond_dttm = get_local_buoy_datetime(day_cond.am.timestamp, reg_info.timezone)
    pm_cond_dttm = get_local_buoy_datetime(day_cond.pm.timestamp, reg_info.timezone)
    data = {
        "region_name": reg_info.full_name,
        "report_local_datetime": reg_dttm,
        "observation": day_cond.observation,
        "am_report": {
            "type": "AM",
            "report_local_datetime": am_cond_dttm,
            "observation": day_cond.am.observation,
            "rating": day_cond.am.rating,
            "min_height": day_cond.am.minHeight,
            "max_height": day_cond.am.maxHeight
        },
        "pm_report": {
            "type": "PM",
            "report_local_datetime": pm_cond_dttm,
            "observation": day_cond.pm.observation,
            "rating": day_cond.pm.rating,
            "min_height": day_cond.pm.minHeight,
            "max_height": day_cond.pm.maxHeight
        }
    }
    return data
