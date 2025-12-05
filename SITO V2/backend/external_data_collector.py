# backend/external_data_collector.py
"""
Questo modulo gestisce la raccolta di dati da sorgenti esterne
- MVD2555 (seriale)
- Altra fonte (HTTP, GPIO, ecc)
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class MVD2555Collector:
    """Raccoglie dati da MVD2555 via seriale"""
    
    def __init__(self):
        self.last_reading: Optional[Dict[str, Any]] = None
        self.is_connected = False
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """
        Legge dati da MVD2555
        In futuro integra con pyserial e comunicazione reale
        """
        try:
            # SIMULAZIONE: In produzione leggerai da seriale
            # import serial
            # self.serial = serial.Serial('/dev/ttyUSB0', 9600)
            
            # Per ora simulo dati
            self.last_reading = {
                "timestamp": datetime.now().isoformat(),
                "source": "MVD2555",
                "tensione": 12.5,      # Volt (es: tensione corda)
                "carico": 500,         # Newton
                "temperatura": 25.3,   # °C
                "status": "OK"
            }
            
            logger.info(f"✅ MVD2555 data collected: {self.last_reading}")
            return self.last_reading
            
        except Exception as e:
            logger.error(f"❌ Errore raccolta MVD2555: {e}")
            return None

class ExternalSourceCollector:
    """Raccoglie dati da altre fonti (HTTP, GPIO, database esterno, ecc)"""
    
    def __init__(self):
        self.last_reading: Optional[Dict[str, Any]] = None
    
    async def collect(self) -> Optional[Dict[str, Any]]:
        """
        Legge dati da fonte esterna
        Es: API esterna, sensore GPIO, database remoto, ecc
        """
        try:
            # SIMULAZIONE: In produzione integra con la vera fonte
            # import requests
            # response = requests.get('https://api-esterna.com/dati')
            
            # Per ora simulo dati
            self.last_reading = {
                "timestamp": datetime.now().isoformat(),
                "source": "EXTERNAL_API",
                "altitudine": 1250,           # Metri
                "coordinate_gps": "43.7102,10.4069",  # Lat,Lon
                "umidita": 65,                # %
                "pressione": 1013.25,         # hPa
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
