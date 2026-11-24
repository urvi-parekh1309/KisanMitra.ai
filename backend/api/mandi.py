from fastapi import APIRouter, Query
from typing import Dict, Any, Optional
from services.mandi_service import mandi_service

router = APIRouter(prefix="/mandi", tags=["Mandi Price Information"])


@router.get("", response_model=Dict[str, Any])
async def get_mandi_prices_endpoint(
    commodity: Optional[str] = Query(default=None, description="Commodity name (Cotton, Soybean, Wheat, Onion, Groundnut)"),
    state: Optional[str] = Query(default=None, description="State name (Maharashtra, Gujarat, Madhya Pradesh)")
):
    """
    Returns authentic Mandi market prices with Min, Max, Modal prices,
    reporting dates, and market comparisons across APMCs.
    """
    return await mandi_service.get_mandi_prices(commodity=commodity, state=state)
