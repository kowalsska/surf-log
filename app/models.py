from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

## SUBMODELS


class Units(BaseModel):
    temperature: str
    tideHeight: str
    swellHeight: str
    waveHeight: str
    windSpeed: str
    pressure: str


class ConditionsAssociated(BaseModel):
    units: dict
    utcOffset: int


class Forecaster(BaseModel):
    name: Optional[str]
    avatar: Optional[str]


class Report(BaseModel):
    timestamp: int
    observation: str
    rating: Optional[str]
    minHeight: int
    maxHeight: int
    plus: bool
    humanRelation: str
    occasionalHeight: Optional[str]


class DailyConditions(BaseModel):
    timestamp: int
    forecastDay: date
    forecaster: Optional[Forecaster]
    human: bool
    observation: str
    am: Report
    pm: Report
    utcOffset: int


class ConditionsData(BaseModel):
    conditions: List[DailyConditions]


class WaveAssociated(BaseModel):
    units: dict
    utcOffset: int


class Surf(BaseModel):
    min: Optional[float]
    max: Optional[float]
    optimalScore: Optional[int]


class Swell(BaseModel):
    height: Optional[float]
    period: Optional[int]
    direction: Optional[float]
    directionMin: Optional[float]
    optimalScore: Optional[int]


class WaveInterval(BaseModel):
    timestamp: int
    probability: Optional[str]
    utcOffset: int
    surf: Surf
    swells: List[Swell]


class WaveData(BaseModel):
    wave: List[WaveInterval]


class Location(BaseModel):
    lat: float
    lon: float


class RatingAssociated(BaseModel):
    location: Location
    runInitializationTimestamp: int


class Rating(BaseModel):
    key: str
    value: float


class RatingInterval(BaseModel):
    timestamp: int
    utcOffset: int
    rating: Rating


class RatingData(BaseModel):
    rating: List[RatingInterval]


class WindAssociated(BaseModel):
    units: Units
    utcOffset: int
    location: Location
    runInitializationTimestamp: int


class WindInterval(BaseModel):
    timestamp: int
    utcOffset: int
    speed: float
    direction: int
    directionType: str
    gust: float
    optimalScore: int


class WindData(BaseModel):
    wind: List[WindInterval]


class TideLocation(BaseModel):
    name: str
    min: float
    max: float
    lon: float
    lat: float
    mean: float


class TideAssociated(BaseModel):
    units: Units
    utcOffset: int
    tideLocation: TideLocation
    runInitializationTimestamp: Optional[int]


class TideInterval(BaseModel):
    timestamp: int
    utcOffset: int
    type: str
    height: float


class TideData(BaseModel):
    tides: List[TideInterval]


class NearbyAssociated(BaseModel):
    units: Units


class BuoyReading(BaseModel):
    timestamp: int
    height: float
    period: int
    direction: int
    swells: List[Swell]


class Buoy(BaseModel):
    id: str
    name: str
    sourceId: str
    latitude: float
    longitude: float
    status: str
    abbrTimezone: str
    latestData: BuoyReading


## TOP LEVEL RESPONSE MODELS


class ConditionsResponse(BaseModel):
    associated: ConditionsAssociated
    data: ConditionsData
    region: str


class NearbyResponse(BaseModel):
    associated: NearbyAssociated
    data: List[Buoy]


class RatingResponse(BaseModel):
    associated: RatingAssociated
    data: RatingData
    spot: str


class TideResponse(BaseModel):
    associated: TideAssociated
    data: TideData
    spot: str


class WaveResponse(BaseModel):
    associated: WaveAssociated
    data: WaveData
    spot: str


class WindResponse(BaseModel):
    associated: WindAssociated
    data: WindData
    spot: str


## OTHER MODELS


class RegionInfo(BaseModel):
    region_id: str
    region_name: str
    full_name: str
    latitude: float
    longitude: float
    timezone: str
    buoy_id: str


class LatestBuoyData(BaseModel):
    name: str
    source_id: str
    buoy_local_datetime: datetime
    wave_height: float
    wave_period: int
    swells: List[Swell]


class ConditionsReport(BaseModel):
    type: str
    report_local_datetime: datetime
    observation: str
    rating: str
    min_height: int
    max_height: int


class RegionalReport(BaseModel):
    region_name: str
    report_local_datetime: datetime
    observation: str
    am_report: Optional[ConditionsReport]
    pm_report: Optional[ConditionsReport]


class WindDataInterval(BaseModel):
    interval_local_datetime: datetime
    speed: float
    direction: int
    direction_type: str
    gust: float
    optimal_score: int


class WindData(BaseModel):
    spot_name: str
    report_local_datetime: datetime
    intervals: List[WindDataInterval]
