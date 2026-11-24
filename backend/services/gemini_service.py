import os
from typing import Dict, Any, List, Optional
from config import settings
from ai.prompts import SYSTEM_PROMPT, build_rag_prompt

try:
    from google import genai
    from google.genai import types
    HAS_NEW_GENAI = True
except Exception:
    HAS_NEW_GENAI = False

try:
    import google.generativeai as legacy_genai
    HAS_LEGACY_GENAI = True
except Exception:
    HAS_LEGACY_GENAI = False


class GeminiService:
    """
    Interfaces with Google Gemini LLM for agricultural question answering.
    Handles grounded prompting with retrieved RAG context, weather, mandi data,
    and multilingual outputs in Marathi, Hindi, Gujarati, and English.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.is_configured = bool(self.api_key and self.api_key != "your_gemini_api_key_here")

        self.client = None
        if self.is_configured:
            self._initialize_client()

    def _initialize_client(self):
        """Initializes the Gemini client."""
        if HAS_NEW_GENAI:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print(f"[GeminiService] Initialized modern google-genai Client (Model: {self.model_name})")
                return
            except Exception as e:
                print(f"[GeminiService] Failed to initialize modern Client: {e}")

        if HAS_LEGACY_GENAI:
            try:
                legacy_genai.configure(api_key=self.api_key)
                print(f"[GeminiService] Initialized legacy google.generativeai (Model: {self.model_name})")
            except Exception as e:
                print(f"[GeminiService] Failed to configure legacy genai: {e}")

    def generate_response(
        self,
        query: str,
        language: str = "en",
        retrieved_context: Optional[Dict[str, Any]] = None,
        weather_info: str = "",
        mandi_info: str = "",
        soil_info: str = ""
    ) -> Dict[str, Any]:
        """
        Generates a grounded, multilingual agricultural response using Gemini.
        """
        context_text = ""
        sources = []
        if retrieved_context:
            context_text = retrieved_context.get("context_text", "")
            sources = retrieved_context.get("sources", [])

        # Build prompt
        full_prompt = build_rag_prompt(
            query=query,
            language=language,
            context_text=context_text,
            sources_count=len(sources),
            weather_info=weather_info,
            mandi_info=mandi_info,
            soil_info=soil_info
        )

        # 1. If Gemini API is configured, call the live model
        if self.is_configured:
            try:
                if HAS_NEW_GENAI and self.client:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.3  # Low temperature for factual grounding
                        )
                    )
                    return {
                        "answer": response.text,
                        "model": self.model_name,
                        "sources": sources,
                        "language": language,
                        "is_live_llm": True
                    }

                elif HAS_LEGACY_GENAI:
                    model = legacy_genai.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=SYSTEM_PROMPT
                    )
                    response = model.generate_content(
                        full_prompt,
                        generation_config={"temperature": 0.3}
                    )
                    return {
                        "answer": response.text,
                        "model": self.model_name,
                        "sources": sources,
                        "language": language,
                        "is_live_llm": True
                    }
            except Exception as e:
                print(f"[GeminiService] Live Gemini API error: {e}. Generating offline grounded response.")

        # 2. Offline RAG Synthesis Fallback
        # When no API key is provided, synthesize response from the retrieved knowledge chunks
        offline_answer = self._synthesize_offline_rag_response(
            query=query,
            language=language,
            context_text=context_text,
            sources=sources,
            weather_info=weather_info
        )

        return {
            "answer": offline_answer,
            "model": "KnowledgeBase-RAG-Synthesizer",
            "sources": sources,
            "language": language,
            "is_live_llm": False,
            "note": "Generated from local verified knowledge base. Add GEMINI_API_KEY in .env for live Gemini 2.5 Flash generations."
        }

    def _synthesize_offline_rag_response(
        self,
        query: str,
        language: str,
        context_text: str,
        sources: List[Dict[str, Any]],
        weather_info: str = ""
    ) -> str:
        """
        Synthesizes an intelligent, grounded response directly from retrieved chunks
        when running in local offline demo mode.
        """
        headers = {
            "mr": {
                "title": "🌾 **किसानमित्र शेती सल्लागार (RAG आधारित सल्ला)**",
                "sources": "📚 **संदर्भित अधिकृत स्रोत (Verified Sources):**",
                "weather": "🌦️ **स्थानिक हवामान सूचना:**",
                "no_docs": "माफ करा, या प्रश्नासाठी थेट संदर्भ ग्रंथालयात उपलब्ध नाही. कृपया स्थानिक कृषी विज्ञान केंद्राशी (KVK) संपर्क साधा."
            },
            "hi": {
                "title": "🌾 **किसानमित्र कृषि सलाहकार (RAG आधारित परामर्श)**",
                "sources": "📚 **सत्यापित संदर्भ स्रोत (Verified Sources):**",
                "weather": "🌦️ **स्थानीय मौसम चेतावनी:**",
                "no_docs": "क्षमा करें, इस प्रश्न के लिए स्थानीय ज्ञानकोष में सीधा संदर्भ उपलब्ध नहीं है। कृपया अपने नजदीकी कृषि विज्ञान केंद्र (KVK) से संपर्क करें।"
            },
            "gu": {
                "title": "🌾 **કિસાનમિત્ર કૃષિ સલાહકાર (RAG આધારિત સલાહ)**",
                "sources": "📚 **પ્રમાણિત સંદર્ભ સ્ત્રોત (Verified Sources):**",
                "weather": "🌦️ **સ્થાનિક હવામાન ચેતવણી:**",
                "no_docs": "માફ કરશો, આ પ્રશ્ન માટે સ્થાનિક સંદર્ભ પુસ્તકાલયમાં સીધી માહિતી ઉપલબ્ધ નથી. કૃપા કરીને નજીકના કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) નો સંપર્ક કરો."
            },
            "en": {
                "title": "🌾 **KisanMitra Agricultural Advisory (Grounded RAG Response)**",
                "sources": "📚 **Verified Agricultural Sources:**",
                "weather": "🌦️ **Local Weather Advisory:**",
                "no_docs": "No specific document matching this query was found in the verified knowledge base. Please consult your local Krishi Vigyan Kendra (KVK)."
            }
        }

        h = headers.get(language, headers["en"])

        if not sources or not context_text:
            return f"{h['title']}\n\n{h['no_docs']}"

        # Clean top excerpt
        top_chunk = sources[0]["snippet"]
        doc_name = sources[0]["document"]
        page_num = sources[0]["page"]

        lines = [
            f"{h['title']}\n",
            f"**प्रश्न / Question:** {query}\n",
            "**तपासलेली माहिती व सल्ला / Recommended Guidance:**\n",
            f"{top_chunk}\n"
        ]

        if weather_info:
            lines.append(f"{h['weather']}\n{weather_info}\n")

        lines.append(f"{h['sources']}")
        for s in sources:
            lines.append(f"- 📄 **{s['document']}** (पान / Page {s['page']}) — *सुसंगतता / Relevance: {int(s['relevance_score']*100)}%*")

        return "\n".join(lines)


gemini_service = GeminiService()
