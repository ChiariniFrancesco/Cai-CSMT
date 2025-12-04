# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from database import init_db
from api import router

# Startup event
def startup_event():
    """Inizializza database all'avvio"""
    init_db()
    print("✅ Database inizializzato")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    startup_event()
    print("🚀 FastAPI server avviato")
    yield
    # Shutdown
    print("🛑 Server fermato")

# Crea FastAPI app
app = FastAPI(
    title="CAI Mountain Gear Testing",
    description="API per gestire configurazioni con preset salvate",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Consenti richieste da React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Includi router API
app.include_router(router)

# 🎯 MONTA REACT STATIC FILES
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
