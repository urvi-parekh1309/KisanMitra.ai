from fastapi import APIRouter, Query
from typing import Dict, Any
from services.weather_service import weather_service

router = APIRouter(prefix="/weather", tags=["Weather Advisory"])


@router.get("", response_model=Dict[str, Any])
async def get_weather_endpoint(
    location: str = Query(default="Pune", description="City, district, or region name")
):
    """
    Returns real-time weather observations, forecasts, and agricultural action advisories.
    """
    return await weather_service.get_weather(location=location)
