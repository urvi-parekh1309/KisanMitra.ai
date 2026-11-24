# 🌾 KisanMitra AI: Multilingual Agritech & Resource Advisory Assistant

> An AI-powered, context-aware agricultural advisory platform empowering Indian farmers with real-time weather alerts, APMC mandi commodity prices, soil health analysis, and trustworthy agronomic recommendations powered by **Retrieval-Augmented Generation (RAG)** and **Google Gemini**.

---

## 🌟 Key Features

* **Real Multilingual RAG Architecture**: Answers are strictly grounded on authentic agricultural publications from the **Indian Council of Agricultural Research (ICAR)** and State Agricultural Universities using **PyMuPDF**, recursive semantic chunking, multilingual embeddings, and **ChromaDB**.
* **4-Language Support**: Seamlessly communicates in **Marathi (मराठी)**, **Hindi (हिन्दी)**, **Gujarati (ગુજરાતી)**, and **English**.
* **Farmer Voice Interaction**: Built-in speech-to-text input in native Indian languages + audio playback (Text-to-Speech) so farmers with varying literacy levels can listen to advice.
* **Live Weather Advisory**: Integrates OpenWeather API observations and forecasts, translating meteorological conditions into actionable spray windows, disease warnings, and irrigation precautions.
* **Authentic Mandi Commodity Prices**: Official AGMARKNET APMC market price tracking across Maharashtra, Gujarat, and Madhya Pradesh with minimum, maximum, and modal price comparisons.
* **Soil & Crop Suitability Engine**: Evaluates soil texture (Black Regur, Alluvial, Red Sandy, Clay Loam), pH levels, and land size to deliver customized crop selection and soil amendment advisories.
* **Grounded Source Attribution**: Every advisory cites the exact document title, page number, and similarity score to prevent AI hallucinations.

---

## 🏗️ System Architecture

```
                                  [ FARMER / USER ]
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   │                                           │
             (Text Input)                                (Voice Mic)
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
                 ┌───────────────────────────────────────────┐
                 │          REACT + VITE FRONTEND            │
                 │  - Multilingual UI (MR / HI / GU / EN)    │
                 │  - Web Speech API (STT / TTS)             │
                 │  - Weather, Mandi, & Soil Dashboard       │
                 └─────────────────────┬─────────────────────┘
                                       │ HTTP REST / JSON
                                       ▼
                 ┌───────────────────────────────────────────┐
                 │              FASTAPI BACKEND              │
                 │  - CORS Middleware & Pydantic Validation  │
                 │  - Unified API Router (/api/v1)           │
                 └──────┬──────────────┬─────────────┬───────┘
                        │              │             │
        ┌───────────────┘              │             └────────────────┐
        ▼                              ▼                              ▼
┌───────────────┐              ┌───────────────┐              ┌───────────────┐
│  Weather API  │              │   Mandi API   │              │ Soil Advisory │
│ (OpenWeather) │              │  (AGMARKNET)  │              │ Rules Engine  │
└───────┬───────┘              └───────┬───────┘              └───────┬───────┘
        │                              │                              │
        └──────────────────────┐       │       ┌──────────────────────┘
                               ▼       ▼       ▼
                        ┌───────────────────────────────┐
                        │    CONTEXT AGGREGATOR LAYER   │
                        └──────────────┬────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RETRIEVAL-AUGMENTED GENERATION (RAG)                  │
│                                                                             │
│  [ICAR PDFs & Guides] ──> [PyMuPDF / pypdf] ──> [Text Preprocessor]         │
│                                                            │                │
│                                                            ▼                │
│  [ChromaDB Vector Store] <── [Multilingual Embedder] <── [Semantic Chunks]  │
│            │                                                                │
│            ▼                                                                │
│  [Top-K Semantic Retriever] ──> [Formatted Grounding Context + Citations]   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
                        ┌───────────────────────────────┐
                        │     GOOGLE GEMINI 2.5 FLASH   │
                        │  - Grounded System Prompt     │
                        │  - Fact-checked Synthesis     │
                        │  - Native Language Generation │
                        └──────────────┬────────────────┘
                                       │
                                       ▼
                 [ Actionable Farm Advisory + Verified Sources ]
```

---

## 📁 Complete File-by-File Codebase Directory

```
agritech-advisor/
├── backend/
│   ├── api/
│   │   ├── chat.py                 # POST /api/chat: Multilingual RAG advisor endpoint
│   │   ├── weather.py              # GET /api/weather: OpenWeather observations & advisories
│   │   ├── mandi.py                # GET /api/mandi: AGMARKNET commodity prices & market comparisons
│   │   ├── soil.py                 # POST /api/soil/advisory: Crop suitability & soil amendment engine
│   │   └── rag.py                  # GET/POST /api/rag: Knowledge base inspection & re-indexing
│   │
│   ├── services/
│   │   ├── gemini_service.py       # Google Gemini LLM wrapper & offline RAG synthesizer
│   │   ├── rag_service.py          # Central RAG orchestrator coordinating loader, splitter & ChromaDB
│   │   ├── weather_service.py      # Weather API client & agronomic impact translator
│   │   ├── mandi_service.py        # Official APMC market data provider
│   │   └── soil_service.py         # Soil profile rules engine & crop suitability matcher
│   │
│   ├── rag/
│   │   ├── document_loader.py      # PDF (PyMuPDF / pypdf) & TXT extractor with Unicode normalization
│   │   ├── text_splitter.py        # RecursiveCharacterTextSplitter with Indic sentence boundary support
│   │   ├── embedding_service.py    # Google text-embedding-004 & multilingual subword vectorizer
│   │   ├── vector_store.py         # Persistent ChromaDB client with pure-Python SQLite fallback
│   │   └── retriever.py            # Multilingual query expander, threshold filtering, & context builder
│   │
│   ├── ai/
│   │   └── prompts.py              # System prompt and strict anti-hallucination grounding templates
│   │
│   ├── knowledge_base/
│   │   ├── documents/
│   │   │   ├── icar_national_crop_handbook.pdf    # 3-page authentic ICAR PDF document
│   │   │   ├── icar_cotton_advisory.txt           # Pink bollworm symptoms & ETL thresholds
│   │   │   ├── soybean_cultivation_and_diseases.txt# Yellow mosaic virus & sowing guidelines
│   │   │   └── wheat_and_groundnut_guide.txt      # Critical irrigation & gypsum nutrition
│   │   └── vector_store/                          # ChromaDB persistent collection on disk
│   │
│   ├── config.py                   # Pydantic BaseSettings environment configuration
│   ├── main.py                     # FastAPI application entry point, CORS, & static SPA serving
│   ├── requirements.txt            # Python dependencies (FastAPI, ChromaDB, PyMuPDF, GenAI)
│   ├── test_rag.py                 # Automated RAG verification test suite
│   └── test_api.py                 # Full-stack API integration test suite
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Header with branding, tab navigation, & language selector
│   │   │   ├── ChatWindow.jsx      # Conversational UI with message bubbles & citation inspector
│   │   │   ├── VoiceInput.jsx      # Speech-to-text mic & Text-to-speech audio reader
│   │   │   ├── WeatherCard.jsx     # Live meteorological dashboard with spray advisories
│   │   │   ├── MandiPriceCard.jsx  # APMC market comparison card with Min/Max/Modal prices
│   │   │   ├── SoilAdvisoryCard.jsx# Interactive soil profile & crop selection calculator
│   │   │   └── KnowledgeBaseModal.jsx# Real-time RAG & ChromaDB inspector modal
│   │   │
│   │   ├── pages/
│   │   │   └── Dashboard.jsx       # Unified responsive farmer dashboard
│   │   ├── services/
│   │   │   └── api.js              # Centralized frontend API client
│   │   ├── locales/
│   │   │   └── translations.js     # Full UI dictionary for Marathi, Hindi, Gujarati, English
│   │   ├── App.jsx                 # Main application component & health monitoring
│   │   ├── main.jsx                # React DOM root entry point
│   │   └── index.css               # Tailwind CSS directives & typography
│   │
│   ├── index.html                  # HTML entry point with Indic Google Fonts
│   ├── vite.config.js              # Vite bundler configuration with backend API proxy
│   ├── tailwind.config.js          # Tailwind CSS theme with agricultural color palette
│   ├── postcss.config.js           # PostCSS configuration
│   └── package.json                # Frontend npm dependencies
│
├── .gitignore                      # Git exclusion rules (venv, node_modules, .env, vector caches)
├── .env.example                    # Environment variable template
└── README.md                       # Comprehensive project documentation
```

---

## 🚀 Quickstart Guide

### Prerequisites
* Python 3.10+ (Tested on Python 3.11)
* Node.js v18+ (Tested on Node v20)
* (Optional) Free Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

---

### Step 1: Clone and Configure Environment

```bash
git clone <repository_url>
cd agritech-advisor

# Create .env from template
cp .env.example .env
```

Edit `.env` to configure your API keys (optional for local demo mode):
```ini
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
DATA_GOV_IN_API_KEY=your_data_gov_in_api_key_here
```

---

### Step 2: Backend Setup & Execution

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run automated RAG and API test suites
python test_rag.py
python test_api.py

# Start FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at:
* Interactive Swagger Docs: `http://localhost:8000/docs`
* API Root: `http://localhost:8000/api/info`
* Health Check: `http://localhost:8000/api/health`

---

### Step 3: Frontend Setup & Execution

In a new terminal:
```bash
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```

Frontend application will open at:
* **`http://localhost:5173`**

---

### Unified Single-Command Mode
Because the React application is pre-built into `frontend/dist/`, running the FastAPI server alone will also serve the complete React application directly at **`http://localhost:8000`**!

---

## 🧪 Automated Testing & Verification

The project includes two automated test suites verifying all core requirements:

### 1. RAG Pipeline Verification (`test_rag.py`)
Tests document extraction, chunking, indexing, and cross-lingual retrieval:
* **Test 1 (Marathi)**: *"कापसावरील गुलाबी बोंडअळीचे नियंत्रण कसे करावे?"*
  * ✅ **PASSED**: Retrieved `icar_cotton_advisory.txt` (Page 1) with Pink Bollworm ETL guidelines.
* **Test 2 (Hindi)**: *"सोयाबीन की बुवाई कब करनी चाहिए और पीला मोजेक वायरस का लक्षण क्या है?"*
  * ✅ **PASSED**: Retrieved `soybean_cultivation_and_diseases.txt` and `icar_national_crop_handbook.pdf`.
* **Test 3 (English)**: *"How can I protect my standing crop during heavy rainfall?"*
  * ✅ **PASSED**: Retrieved `icar_national_crop_handbook.pdf` (Page 3) with waterlogging drainage protocols.
* **Test 4 (Negative Out-of-Domain Test)**: *"How do I replace the clutch plate in a Mahindra 575 tractor?"*
  * ✅ **PASSED**: Correctly identified zero relevant agronomic context; safely rejected out-of-domain query.

### 2. Full-Stack API Integration Suite (`test_api.py`)
* `GET /` — Verified React SPA static serving.
* `GET /api/health` — Verified ChromaDB status (22 indexed chunks).
* `GET /api/weather` — Verified meteorological observations & spray window alerts.
* `GET /api/mandi` — Verified APMC price records and comparisons.
* `POST /api/soil/advisory` — Verified crop suitability analysis for Black Regur soil.
* `POST /api/chat` (Marathi & Hindi) — Verified grounded advisory synthesis with source citations.

---

## 🌐 Deployment Instructions

### Deploying Backend to Render
1. Connect your GitHub repository to [Render](https://render.com/).
2. Create a **Web Service**.
3. Set the Root Directory to `backend`.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables: `GEMINI_API_KEY`, `OPENWEATHER_API_KEY`.

### Deploying Frontend to Vercel
1. Connect your repository to [Vercel](https://vercel.com/).
2. Set Root Directory to `frontend`.
3. Framework Preset: `Vite`.
4. Build Command: `npm run build`
5. Output Directory: `dist`
6. Set `VITE_API_URL` to your Render backend URL.

---

## 📜 Academic & Agronomic Disclaimer
This system provides educational and advisory recommendations derived from published ICAR and State Agricultural University research. For commercial crop decisions, pesticide applications, and soil fertility management, always verify with local agricultural extension officers and accredited laboratory Soil Health Card tests.
