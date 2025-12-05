# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database import init_db
from api import router
from tasks import start_scheduler, stop_scheduler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Avvio server...")
    init_db()
    start_scheduler()  # 🔴 AVVIA SCHEDULER
    logger.info("✅ Server pronto")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arresto server...")
    stop_scheduler()  # 🔴 FERMA SCHEDULER
    logger.info("❌ Server arrestato")

app = FastAPI(
    title="MVD2555 Configuration System - Fase 2",
    description="API con raccolta dati + Firebase",
    version="2.0.0",
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
