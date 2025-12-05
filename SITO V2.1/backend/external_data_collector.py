# backend/external_data_collector.py
"""
Raccolta di dati da sorgenti esterne (versione SIMULATA per testing)
- MVD2555 (seriale)
- Altra fonte (HTTP, GPIO, ecc)

Per testing, genera dati fake che cambiano leggermente ogni volta
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import random

logger = logging.getLogger(__name__)

class MVD2555Collector:
    """Simula la raccolta di dati da MVD2555"""
    
    def __init__(self):
        self.last_reading: Optional[Dict[str, Any]] = None
        self.is_connected = True
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """
        Legge dati da MVD2555 (SIMULATO per testing)
        In futuro: integra con pyserial e comunicazione reale
        """
        try:
            # SIMULAZIONE: Dati che cambiano leggermente
            self.last_reading = {
                "timestamp": datetime.now().isoformat(),
                "source": "MVD2555",
                "tensione": round(12.0 + random.uniform(-0.5, 0.5), 2),  # Varia tra 11.5-12.5V
                "carico": random.randint(450, 550),  # Varia tra 450-550 N
                "temperatura": round(25.0 + random.uniform(-2, 2), 1),   # Varia tra 23-27°C
                "status": "OK"
            }
            
            logger.info(f"✅ MVD2555 data collected: {self.last_reading}")
            return self.last_reading
            
        except Exception as e:
            logger.error(f"❌ Errore raccolta MVD2555: {e}")
            return None

class ExternalSourceCollector:
    """Simula la raccolta di dati da fonte esterna"""
    
    def __init__(self):
        self.last_reading: Optional[Dict[str, Any]] = None
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """
        Legge dati da fonte esterna (SIMULATO per testing)
        In futuro: integra con API esterna, sensori GPIO, ecc
        """
        try:
            # SIMULAZIONE: Dati che cambiano leggermente
            self.last_reading = {
                "timestamp": datetime.now().isoformat(),
                "source": "EXTERNAL_API",
                "altitudine": random.randint(1200, 1300),              # Varia tra 1200-1300m
                "coordinate_gps": f"{43.7 + random.uniform(-0.01, 0.01):.4f},{10.4 + random.uniform(-0.01, 0.01):.4f}",
                "umidita": random.randint(60, 75),                     # Varia tra 60-75%
                "pressione": round(1013.0 + random.uniform(-5, 5), 2), # Varia 1008-1018 hPa
                "status": "OK"
            }
            
            logger.info(f"✅ External source data collected: {self.last_reading}")
            return self.last_reading
            
        except Exception as e:
            logger.error(f"❌ Errore raccolta fonte esterna: {e}")
            return None

class DataAggregator:
    """
    Combina dati da multiple sorgenti
    Quando ENTRAMBI i dati sono disponibili, li combina e ritorna
    """
    
    def __init__(self):
        self.mvd_collector = MVD2555Collector()
        self.external_collector = ExternalSourceCollector()
        self.last_combined: Optional[Dict[str, Any]] = None
    
    async def get_combined_data(self) -> Optional[Dict[str, Any]]:
        """
        Raccoglie dati da ENTRAMBE le sorgenti in parallelo
        Ritorna i dati combinati quando ENTRAMBI disponibili
        """
        try:
            # Esegui entrambe le raccolte IN PARALLELO con asyncio.gather
            mvd_data, external_data = await asyncio.gather(
                self.mvd_collector.collect(),
                self.external_collector.collect(),
                return_exceptions=True
            )
            
            # Se uno dei due fallisce, ritorna None
            if mvd_data is None or external_data is None:
                logger.warning("⚠️ Una delle fonti non ha dati disponibili")
                return None
            
            # Combina i dati
            self.last_combined = {
                "timestamp": datetime.now().isoformat(),
                "combined_from": "MVD2555 + EXTERNAL_SOURCE",
                "mvd2555": mvd_data,
                "external_source": external_data,
                "status": "COMPLETE"
            }
            
            logger.info(f"✅ Dati combinati: {self.last_combined}")
            return self.last_combined
            
        except Exception as e:
            logger.error(f"❌ Errore combinazione dati: {e}")
            return None
