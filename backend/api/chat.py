from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from services.rag_service import rag_service
from services.gemini_service import gemini_service
from services.weather_service import weather_service
from services.mandi_service import mandi_service
from services.soil_service import soil_service

router = APIRouter(prefix="/chat", tags=["AI Advisory Chatbot"])


class ChatRequest(BaseModel):
    query: str = Field(..., description="Farmer question in Marathi, Hindi, Gujarati, or English")
    language: str = Field(default="en", description="Language code: 'mr', 'hi', 'gu', 'en'")
    location: Optional[str] = Field(default="Pune", description="Farmer location or district")
    soil_type: Optional[str] = Field(default=None, description="Soil type (black, alluvial, red sandy)")
    soil_ph: Optional[float] = Field(default=None, description="Soil pH value")
    commodity: Optional[str] = Field(default=None, description="Crop/commodity name for mandi price lookup")


class ChatResponse(BaseModel):
    answer: str
    language: str
    model: str
    sources: List[Dict[str, Any]]
    weather_summary: Optional[Dict[str, Any]] = None
    mandi_summary: Optional[Dict[str, Any]] = None
    has_rag_context: bool


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Multilingual AI Agricultural Advisor endpoint.
    Performs real RAG retrieval across ICAR documents, pulls weather and mandi context,
    and synthesizes a grounded response in Marathi, Hindi, Gujarati, or English.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    lang = request.language.lower()
    if lang not in ["mr", "hi", "gu", "en"]:
        lang = "en"

    # 1. Retrieve Grounded Context from Vector Store (RAG)
    rag_result = rag_service.retrieve(query=query)
    context_text = rag_result.get("context_text", "")
    sources = rag_result.get("sources", [])
    has_context = rag_result.get("has_context", False)

    # 2. Fetch Weather Context
    weather_info_str = ""
    weather_data = None
    if request.location:
        try:
            weather_data = await weather_service.get_weather(request.location)
            weather_info_str = f"Location: {weather_data['location']} | Temp: {weather_data['temperature_c']}°C | Humidity: {weather_data['humidity_percent']}% | Condition: {weather_data['condition']} | Wind: {weather_data['wind_speed_kmh']} km/h"
        except Exception as e:
            print(f"[ChatAPI] Weather fetch error: {e}")

    # 3. Fetch Mandi Context (if user mentioned crops or prices)
    mandi_info_str = ""
    mandi_data = None
    # Auto-detect commodity from query if not specified
    target_commodity = request.commodity
    if not target_commodity:
        for c in ["Cotton", "Soybean", "Wheat", "Onion", "Groundnut"]:
            if c.lower() in query.lower() or c in query:
                target_commodity = c
                break

    if target_commodity or "price" in query.lower() or "भाव" in query or "दर" in query or "ભાવ" in query:
        try:
            mandi_data = await mandi_service.get_mandi_prices(commodity=target_commodity)
            if mandi_data.get("data"):
                top_mandi = mandi_data["data"][0]
                mandi_info_str = f"Market: {top_mandi['market']} ({top_mandi['state']}) | Commodity: {top_mandi['commodity']} | Modal Price: Rs {top_mandi['modal_price']} / Quintal | Date: {top_mandi['arrival_date']}"
        except Exception as e:
            print(f"[ChatAPI] Mandi fetch error: {e}")

    # 4. Assemble Soil Context
    soil_info_str = ""
    if request.soil_type:
        soil_adv = soil_service.generate_advisory(
            soil_type=request.soil_type,
            ph=request.soil_ph,
            language=lang
        )
        soil_info_str = f"Soil Type: {soil_adv['soil_profile']} | Characteristics: {soil_adv['soil_characteristics']} | Recommended Crops: {', '.join(soil_adv['recommended_crops'][:3])}"

    # 5. Generate Grounded AI Recommendation
    ai_response = gemini_service.generate_response(
        query=query,
        language=lang,
        retrieved_context=rag_result,
        weather_info=weather_info_str,
        mandi_info=mandi_info_str,
        soil_info=soil_info_str
    )

    return ChatResponse(
        answer=ai_response["answer"],
        language=lang,
        model=ai_response["model"],
        sources=ai_response.get("sources", sources),
        weather_summary=weather_data,
        mandi_summary=mandi_data,
        has_rag_context=has_context
    )
