# backend/main.py
"""
FastAPI main app - Fase 2 con File Storage
NO scheduler per testing (i dati si raccolgono on-demand con POST)
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database import init_db
from api import router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Avvio server...")
    init_db()
    logger.info("✅ Server pronto")
    logger.info("📁 Dati salvati in: ./data/combined_data.jsonl")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arresto server...")
    logger.info("❌ Server arrestato")

app = FastAPI(
    title="MVD2555 Configuration System - Fase 2 Testing",
    description="API con raccolta dati + salvataggio file TXT",
    version="2.2.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router)

# React static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
