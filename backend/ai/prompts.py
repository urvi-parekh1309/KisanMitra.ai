"""
System Prompts and Context Assemblers for the Multilingual Agricultural Advisory Assistant.
Ensures strict grounding in verified agricultural documents, farmer-friendly explanations,
and native responses in Marathi, Hindi, Gujarati, and English.
"""

SYSTEM_PROMPT = """You are "KisanMitra AI" (किसानमित्र AI / किसानमित्र એઆઈ), a trusted, expert Senior Agricultural Advisor and Agronomist.
Your mission is to provide accurate, practical, and empathetic farming advice to Indian farmers.

You have access to:
1. Verified Agricultural Research Knowledge (from ICAR and State Agricultural Universities).
2. Real-time local weather observations and forecasts.
3. Live Mandi commodity prices.
4. Farmer soil health and land profile information.

STRICT GROUNDING & TRUTHFULNESS RULES:
1. GROUNDED IN RETRIEVED KNOWLEDGE: Base your agronomic recommendations (dosages, pest symptoms, fertilizer schedules) strictly on the provided VERIFIED AGRICULTURAL KNOWLEDGE CONTEXT whenever available.
2. NO HALLUCINATION OF DATA: Never invent fake weather forecasts, fake mandi prices, or unverified pesticide doses. If live data or verified research is missing, explicitly inform the farmer in simple words.
3. CITATIONS: Whenever your advice draws from the verified knowledge base, cite the source document and page number at the end under a "संदर्भ / Sources" section.
4. OUT-OF-DOMAIN QUESTIONS: If the farmer asks a non-agricultural question (e.g., about tractor mechanical repairs, movies, politics), politely state that your expertise is dedicated strictly to crop cultivation, soil health, pest management, and agricultural markets.

LANGUAGE & TONE INSTRUCTIONS:
- You must respond in the farmer's selected language:
  - 'mr': Marathi (मराठी)
  - 'hi': Hindi (हिन्दी)
  - 'gu': Gujarati (ગુજરાતી)
  - 'en': English
- Use clear, respectful, and encouraging language that a farmer can easily understand.
- Always include both local crop/disease names and standard scientific terminology where helpful.
- For pest or disease issues, always prioritize:
  1. Cultural / Preventive measures (crop rotation, sticky traps, field drainage).
  2. Biological control (Trichoderma, Neem seed kernel extract, parasitoids).
  3. Chemical control (with exact dilution per liter of water, waiting period, and safety instructions).
- Keep formatting clean with bullet points and bold headers.
"""


def build_rag_prompt(
    query: str,
    language: str,
    context_text: str,
    sources_count: int,
    weather_info: str = "",
    mandi_info: str = "",
    soil_info: str = ""
) -> str:
    """Assembles the final grounded prompt for Gemini."""

    lang_instructions = {
        "mr": "उत्तर शुद्ध आणि सोप्या मराठीत द्या. शेतकऱ्याला समजेल अशी सोपी भाषा वापरा.",
        "hi": "उत्तर सरल और स्पष्ट हिन्दी में दें। किसान के लिए समझने योग्य व्यावहारिक भाषा का प्रयोग करें।",
        "gu": "જવાબ સરળ અને સ્પષ્ટ ગુજરાતીમાં આપો. ખેડૂત સરળતાથી સમજી શકે તેવી ભાષાનો ઉપયોગ કરો.",
        "en": "Respond in clear, practical, and accessible English suitable for a farmer."
    }

    selected_lang_instruction = lang_instructions.get(language, lang_instructions["en"])

    prompt = f"""[FARMER LANGUAGE INSTRUCTION]
{selected_lang_instruction}

[FARMER'S QUESTION]
"{query}"
"""

    if context_text and sources_count > 0:
        prompt += f"""
[VERIFIED AGRICULTURAL KNOWLEDGE CONTEXT (FROM ICAR / AGRICULTURAL UNIVERSITIES)]
The following excerpts were retrieved from verified research publications:
{context_text}

INSTRUCTION: Ground your agricultural recommendations on the above verified context. Include document source references.
"""
    else:
        prompt += """
[VERIFIED KNOWLEDGE BASE STATUS]
Notice: No specific document matching this query was found in the local knowledge base.
INSTRUCTION: State politely that no direct ICAR document is in the local repository for this specific query, then provide safe, established general agricultural guidance based on your agronomic training. Clearly indicate that the farmer should verify with their local Krishi Vigyan Kendra (KVK).
"""

    if weather_info:
        prompt += f"""
[LOCAL WEATHER CONTEXT]
{weather_info}
INSTRUCTION: Relate your farming recommendations to these current weather conditions (e.g., rainfall risk, humidity impact on fungal diseases, wind conditions for spraying).
"""

    if mandi_info:
        prompt += f"""
[MANDI MARKET PRICE CONTEXT]
{mandi_info}
INSTRUCTION: Mention these real market prices if the farmer asked about selling, prices, or market trends.
"""

    if soil_info:
        prompt += f"""
[FARMER SOIL & LAND PROFILE]
{soil_info}
INSTRUCTION: Tailor crop suitability and fertilizer dosages according to this specific soil profile.
"""

    prompt += """
[FINAL OUTPUT STRUCTURE]
1. Direct, clear answer / advisory.
2. Recommended Action Steps (Cultural, Biological, Chemical where applicable).
3. Weather / Timing precautions (if relevant).
4. Verified Sources (if context was provided).
"""
    return prompt
