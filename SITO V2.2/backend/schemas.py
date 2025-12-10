# backend/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ConfigurationCreate(BaseModel):
    """Schema per CREARE/AGGIORNARE una configurazione"""
    nome_preset: str
    corda: str
    assicuratore: str
    operatore: str

class ConfigurationResponse(BaseModel):
    """Schema per RISPONDERE con una configurazione"""
    id: int
    nome_preset: str
    corda: str
    assicuratore: str
    operatore: str
    data_creazione: datetime
    data_aggiornamento: datetime
    
    class Config:
        from_attributes = True  # Converte SQLAlchemy model a Pydantic

class SubmitFormData(BaseModel):
    """Schema per il form da React"""
    corda: str
    assicuratore: str
    operatore: str
    salva_come_preset: Optional[str] = None  # Se ha un valore, salva come preset
