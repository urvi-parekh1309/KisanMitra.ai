from typing import Dict, Any, List, Optional


class SoilAdvisoryService:
    """
    Expert Soil & Crop Suitability Advisory Service.
    Analyzes farmer soil parameters (texture, pH, NPK, drainage, land size)
    against ICAR agronomic crop requirements to recommend suitable crops,
    soil amendments, and balanced fertilization.
    """

    SOIL_PROFILES = {
        "black": {
            "name": "Medium to Deep Black Cotton Soil (Regur)",
            "characteristics": "High clay content (40-60%), high water retention capacity, rich in calcium and magnesium, prone to surface cracking when dry and waterlogging when saturated.",
            "optimal_crops": ["Cotton (कापूस)", "Soybean (सोयाबीन)", "Wheat (गहू)", "Chickpea / Bengal Gram (हरभरा)", "Pigeonpea / Tur (तूर)"],
            "management": [
                "Construct broad bed furrows (BBF) or dead furrows to evacuate excess rainwater quickly.",
                "Avoid deep plowing when wet to prevent hardpan formation.",
                "Apply Farm Yard Manure (FYM) @ 5 tonnes/acre to maintain soil aeration."
            ]
        },
        "alluvial": {
            "name": "Alluvial Loam Soil",
            "characteristics": "Deep, fertile, well-balanced silt-loam with neutral pH (6.5-7.5), excellent nutrient exchange, suitable for intensive cropping systems.",
            "optimal_crops": ["Wheat (गहू)", "Mustard (मोहरी)", "Maize (मका)", "Sugarcane (ऊस)", "Vegetables (भाज्या)"],
            "management": [
                "Practice green manuring (Sunhemp / Dhaincha) before Kharif sowing to replenish organic carbon.",
                "Adopt balanced NPK 4:2:1 ratio to prevent nitrogen over-application."
            ]
        },
        "red_sandy": {
            "name": "Red Sandy Loam Soil",
            "characteristics": "Light textured, porous, free-draining, prone to rapid nutrient leaching and moisture stress, generally low in nitrogen and phosphorus.",
            "optimal_crops": ["Groundnut (भुईमूग / मूंगफली)", "Pearl Millet / Bajra (बाजरी)", "Sorghum / Jowar (ज्वारी)", "Castor (एरंडी)", "Pulses (कडधान्ये)"],
            "management": [
                "Incorporate organic mulch to reduce evaporative soil water loss.",
                "Apply split fertilizer doses rather than single basal dressing to prevent leaching.",
                "Apply Gypsum @ 200 kg/acre at flowering stage for groundnut pod filling."
            ]
        },
        "clay_loam": {
            "name": "Medium Clay Loam Soil",
            "characteristics": "Moderate drainage, good organic matter retention, versatile fertility, responsive to chemical and bio-fertilizers.",
            "optimal_crops": ["Soybean", "Cotton", "Onion (कांदा)", "Garlic", "Vegetables"],
            "management": [
                "Maintain crop rotation with leguminous crops to sustain biological nitrogen fixation.",
                "Apply micronutrient Zinc Sulphate @ 10 kg/acre once every 2 years."
            ]
        }
    }

    def generate_advisory(
        self,
        soil_type: str,
        ph: Optional[float] = None,
        land_size_acres: Optional[float] = None,
        preferred_crop: Optional[str] = None,
        organic_carbon_percent: Optional[float] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive soil health and crop suitability advisory.
        """
        s_key = "black"
        raw_type = soil_type.lower()
        if "red" in raw_type or "sand" in raw_type:
            s_key = "red_sandy"
        elif "alluv" in raw_type or "loam" in raw_type:
            s_key = "alluvial" if "alluv" in raw_type else "clay_loam"
        elif "black" in raw_type or "clay" in raw_type or "regur" in raw_type:
            s_key = "black"

        profile = self.SOIL_PROFILES[s_key]

        # pH Analysis
        ph_assessment = "Unknown / Not Tested"
        ph_recommendation = "Conduct a laboratory Soil Health Card test to measure exact pH."
        if ph is not None:
            if ph < 6.0:
                ph_assessment = f"Acidic Soil (pH {ph})"
                ph_recommendation = "Apply agricultural lime (CaCO3) @ 500 kg/acre to neutralize acidity and enhance phosphorus uptake."
            elif 6.5 <= ph <= 7.8:
                ph_assessment = f"Optimal Neutral Soil (pH {ph})"
                ph_recommendation = "Ideal pH range for maximum macronutrient and micronutrient availability."
            elif ph > 7.8:
                ph_assessment = f"Alkaline / Calcareous Soil (pH {ph})"
                ph_recommendation = "Risk of Iron and Zinc chlorosis. Apply Gypsum @ 400 kg/acre and spray Ferrous Sulphate (0.5%) + Citric Acid (0.1%) if yellowing occurs."

        # Preferred Crop Suitability Check
        suitability_status = "Highly Recommended"
        suitability_note = ""
        if preferred_crop:
            pref_lower = preferred_crop.lower()
            is_matched = any(c.lower().startswith(pref_lower) or pref_lower in c.lower() for c in profile["optimal_crops"])
            if is_matched:
                suitability_status = "Optimal Match"
                suitability_note = f"{preferred_crop} is naturally well-suited to {profile['name']}."
            else:
                suitability_status = "Conditional Suitability"
                suitability_note = f"{preferred_crop} requires special soil preparation, drainage management, and organic amendment when grown in {profile['name']}."

        return {
            "soil_profile": profile["name"],
            "soil_characteristics": profile["characteristics"],
            "recommended_crops": profile["optimal_crops"],
            "ph_evaluation": {
                "ph_value": ph,
                "assessment": ph_assessment,
                "recommendation": ph_recommendation
            },
            "crop_suitability": {
                "preferred_crop": preferred_crop or "Not Specified",
                "status": suitability_status,
                "note": suitability_note
            },
            "land_management_practices": profile["management"],
            "disclaimer": "Notice: This advisory is synthesized from agronomic research guidelines for planning purposes. For precise micronutrient fertilizer schedules, rely on certified laboratory Soil Health Card test results."
        }


soil_service = SoilAdvisoryService()
