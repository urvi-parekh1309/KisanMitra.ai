import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings, PROJECT_ROOT
from services.rag_service import rag_service
from services.gemini_service import gemini_service

# Import API routers
from api.chat import router as chat_router
from api.weather import router as weather_router
from api.mandi import router as mandi_router
from api.soil import router as soil_router
from api.rag import router as rag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: Auto-initializes the RAG knowledge base on startup."""
    print("=" * 70)
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 70)
    try:
        init_stats = rag_service.initialize()
        print(f"[Startup] RAG Knowledge Base ready: {init_stats}")
    except Exception as e:
        print(f"[Startup] Warning: RAG auto-initialization error: {e}")
    yield
    print("[Shutdown] Server shutting down cleanly.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Multilingual Agricultural Advisory and Resource Assistant using Gemini and RAG.",
    lifespan=lifespan
)

# Configure CORS for React frontend
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
if "*" not in origins:
    origins.extend(["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api prefix
app.include_router(chat_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(mandi_router, prefix="/api")
app.include_router(soil_router, prefix="/api")
app.include_router(rag_router, prefix="/api")


@app.get("/api/info")
def api_info():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
        "supported_languages": ["mr (Marathi)", "hi (Hindi)", "gu (Gujarati)", "en (English)"],
        "modules": {
            "chat": "/api/chat",
            "weather": "/api/weather",
            "mandi": "/api/mandi",
            "soil": "/api/soil/advisory",
            "rag": "/api/rag/status"
        }
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "rag_ready": rag_service.get_status().get("is_ready", False),
        "total_chunks": rag_service.get_status().get("total_chunks", 0),
        "gemini_configured": gemini_service.is_configured
    }


# Mount compiled React frontend if present
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    @app.get("/")
    def fallback_root():
        return api_info()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
