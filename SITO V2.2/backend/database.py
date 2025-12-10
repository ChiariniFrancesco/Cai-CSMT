# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os

# 🎯 Database URL - SQLite file nel backend
DATABASE_URL = "sqlite:///./data.db"

# Crea engine SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Importante per SQLite + FastAPI
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli
Base = declarative_base()

def get_db():
    """Dependency injection per database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Crea tutte le tabelle"""
    Base.metadata.create_all(bind=engine)
