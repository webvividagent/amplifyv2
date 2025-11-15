from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import Base, engine
from config import settings
from routes import auth_router, repositories_router, chat_router, models_router
from routes.clone import router as clone_router
from services.tier_config import tier_config
from services.model_selector import model_selector
import logging
from pathlib import Path
import os

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Amplify API",
    description="AI-powered code amplification engine - Powered by Ollama",
    version="0.1.0"
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(repositories_router)
app.include_router(chat_router)
app.include_router(models_router)
app.include_router(clone_router)

@app.get("/favicon.svg")
async def favicon():
    favicon_path = Path(__file__).parent.parent / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/svg+xml")
    return {"error": "favicon not found"}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Coding Agent API")
    logger.info(f"System tier: {tier_config.get_tier_str()}")
    logger.info(f"Tier-specific models: {tier_config.get_amplify_models_for_tier()}")
    await model_selector.initialize()
    logger.info(f"Available amplify models: {model_selector.get_available_amplify_models()}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Coding Agent API")

@app.get("/clone")
async def clone_ui():
    """Serve the Amplify cloning UI."""
    template_path = Path(__file__).parent / "templates" / "clone.html"
    if template_path.exists():
        return FileResponse(template_path, media_type="text/html")
    return {"error": "Clone UI not found"}

@app.get("/chat")
async def chat_ui():
    """Serve the Amplify chat UI."""
    template_path = Path(__file__).parent / "templates" / "chat.html"
    if template_path.exists():
        return FileResponse(template_path, media_type="text/html")
    return {"error": "Chat UI not found"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
