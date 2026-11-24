from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from services.soil_service import soil_service

router = APIRouter(prefix="/soil", tags=["Soil and Crop Advisory"])


class SoilAdvisoryRequest(BaseModel):
    soil_type: str = Field(..., description="Soil type (black, alluvial, red_sandy, clay_loam)")
    ph: Optional[float] = Field(default=None, description="Soil pH value if known")
    land_size_acres: Optional[float] = Field(default=None, description="Land size in acres")
    preferred_crop: Optional[str] = Field(default=None, description="Preferred crop (Cotton, Soybean, Wheat, etc.)")
    organic_carbon_percent: Optional[float] = Field(default=None, description="Organic carbon percentage")
    language: str = Field(default="en", description="Language code: mr, hi, gu, en")


@router.post("/advisory", response_model=Dict[str, Any])
async def get_soil_advisory_endpoint(request: SoilAdvisoryRequest):
    """
    Evaluates soil parameters and generates tailored crop suitability,
    soil amendment advisories, and balanced nutrient management schedules.
    """
    return soil_service.generate_advisory(
        soil_type=request.soil_type,
        ph=request.ph,
        land_size_acres=request.land_size_acres,
        preferred_crop=request.preferred_crop,
        organic_carbon_percent=request.organic_carbon_percent,
        language=request.language
    )
