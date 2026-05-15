from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CityResponse(BaseModel):
    name: str
    lat: float
    lon: float

class PulseResponse(BaseModel):
    city: str
    temperature: float
    humidity: int
    condition: str
    aqi: Optional[int]
    pulse_score: Optional[float]
    weather_score: Optional[float]
    air_score: Optional[float]
    timestamp: datetime

class SnapshotResponse(BaseModel):
    timestamp: datetime
    temperature: float
    humidity: int
    condition: str
    aqi: Optional[int]

class HistoryResponse(BaseModel):
    city: str
    hours: int
    snapshots: list[SnapshotResponse]

class DashboardCity(BaseModel):
    city: str
    lat: float
    lon: float
    pulse_score: float
    temperature: float
    condition: str
    aqi: Optional[int]

class DashboardResponse(BaseModel):
    cities: list[DashboardCity]