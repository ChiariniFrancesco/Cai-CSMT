# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from datetime import datetime
from database import Base

class ConfigurationMemory(Base):
    """Model per memorizzare le configurazioni salvate"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_preset = Column(String, unique=True, index=True)  # Nome della preset
    corda = Column(String)                                  # Valore corda
    assicuratore = Column(String)                          # Valore assicuratore
    operatore = Column(String)                             # Nome operatore
    data_creazione = Column(DateTime, default=datetime.now)
    data_aggiornamento = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<ConfigurationMemory id={self.id} nome={self.nome_preset}>"
