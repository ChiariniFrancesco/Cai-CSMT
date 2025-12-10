"""
backend/sensor_monitor.py - V2.2 CORRETTO (CON LOOP DI LETTURA)
Monitor per ascolto CONTINUO del sensore MVD2555 collegato al Raspberry

ADESSO: Loop che legge ogni 2ms e accumula i dati!
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import random
import threading
import time

logger = logging.getLogger(__name__)

class SensorMonitor:
    """
    Monitora il sensore MVD2555 collegato fisicamente al Raspberry
    
    FLUSSO:
    1. CONFERMA form → start_monitoring()
       └─ Avvia THREAD in background che legge ogni 2ms
    2. Backend ASCOLTA continuamente il sensore
    3. Operatore effettua caduta
    4. Operatore preme "HO FATTO LA CADUTA" → stop_monitoring()
    5. Backend analizza dati e trova picco
    """
    
    def __init__(self):
        self.is_monitoring = False
        self.power_readings: list = []
        self.start_time: Optional[float] = None
        self.config: Dict[str, Any] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        
    def set_config(self, corda: str, assicuratore: str, operatore: str):
        """Salva la configurazione"""
        self.config = {
            "corda": corda,
            "assicuratore": assicuratore,
            "operatore": operatore
        }
        logger.info(f"📋 Configurazione set: {self.config}")
    
    def start_monitoring(self):
        """
        INIZIO ASCOLTO sensore MVD2555
        
        Avvia UN THREAD in background che legge il sensore ogni 2ms
        Il thread accumula i dati in self.power_readings
        """
        if self.is_monitoring:
            logger.warning("⚠️ Monitoraggio già in corso")
            return
        
        self.is_monitoring = True
        self.power_readings = []
        self.start_time = time.time()
        
        logger.info(f"""
        🔊 ===============================
        🔊 INIZIO ASCOLTO SENSORE MVD2555
        🔊 ===============================
        🔊 Timestamp inizio: {datetime.now().isoformat()}
        🔊 Configurazione:
        🔊   - Corda: {self.config.get('corda')}
        🔊   - Assicuratore: {self.config.get('assicuratore')}
        🔊   - Operatore: {self.config.get('operatore')}
        🔊 ===============================
        """)
        
        # ✅ AVVIA THREAD DI LETTURA IN BACKGROUND
        self.monitoring_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("🚀 Thread di lettura sensore avviato")
    
    def _read_loop(self):
        """
        LOOP IN BACKGROUND che legge il sensore ogni 2ms
        Accumula i dati finché is_monitoring == True
        """
        logger.info("🔄 Loop di lettura avviato")
        
        while self.is_monitoring:
            try:
                # Leggi un valore dal sensore (SIMULATO o REALE)
                power = self.read_sensor()
                
                # Accumula nel record
                self.add_reading(power)
                
                # Attendi 2ms prima della prossima lettura
                time.sleep(0.002)
                
            except Exception as e:
                logger.error(f"❌ Errore in loop lettura: {e}")
                break
        
        logger.info(f"🛑 Loop di lettura terminato. Letture totali: {len(self.power_readings)}")
    
    def read_sensor(self) -> float:
        """
        Legge un valore dal sensore MVD2555
        
        SIMULAZIONE: genera dati fake realistici
        REALE: legge da pyserial
        """
        
        # ========== SIMULAZIONE ==========
        # Baseline potenza (20-70 N a riposo)
        basePower = random.random() * 50 + 20
        
        # Rumore casuale ±50N
        noisePower = basePower + (random.random() * 100 - 50)
        
        # Assicura range 0-500 N
        power = max(0, min(500, noisePower))
        
        return power
    
    def add_reading(self, power: float):
        """Aggiunge una lettura al record"""
        if not self.is_monitoring:
            return
        
        reading = {
            "timestamp": time.time(),
            "value": round(power, 2)
        }
        
        self.power_readings.append(reading)
    
    def stop_monitoring(self) -> Optional[Dict[str, Any]]:
        """
        FINE ASCOLTO sensore
        Operatore ha premuto "HO FATTO LA CADUTA"
        
        Ferma il thread e analizza i dati raccolti
        """
        
        if not self.is_monitoring:
            logger.warning("⚠️ Monitoraggio non in corso")
            return None
        
        self.is_monitoring = False
        
        # Aspetta che il thread termini (max 100ms)
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=0.1)
            logger.info("✅ Thread di lettura terminato")
        
        logger.info(f"""
        ⛔ ===============================
        ⛔ FINE ASCOLTO SENSORE MVD2555
        ⛔ ===============================
        ⛔ Timestamp fine: {datetime.now().isoformat()}
        ⛔ Letture totali RACCOLTE: {len(self.power_readings)}
        ⛔ ===============================
        """)
        
        # Analizza i dati raccolti
        if len(self.power_readings) == 0:
            logger.warning("⚠️ Nessun dato raccolto dal sensore")
            return None
        
        # Trova il picco massimo
        max_power = 0
        max_index = 0
        max_timestamp = None
        
        for i, reading in enumerate(self.power_readings):
            if reading['value'] > max_power:
                max_power = reading['value']
                max_index = i
                max_timestamp = reading['timestamp']
        
        # Calcola offset in ms dalla caduta
        offset_ms = int((max_timestamp - self.start_time) * 1000)
        
        # Durata totale ascolto
        durata_ms = int((self.power_readings[-1]['timestamp'] - self.start_time) * 1000)
        
        logger.info(f"""
        📊 ANALISI COMPLETATA:
        ├─ Letture totali: {len(self.power_readings)}
        ├─ Picco massimo: {max_power:.2f} N
        ├─ Indice picco: {max_index}
        ├─ Timestamp picco: {datetime.fromtimestamp(max_timestamp).isoformat()}
        ├─ Offset dalla caduta: {offset_ms}ms
        ├─ Durata ascolto: {durata_ms}ms
        └─ Status: ✅ CADUTA RILEVATA
        """)
        
        # Torna il risultato dell'analisi
        return {
            "letture_totali": len(self.power_readings),
            "picco_potenza_N": round(max_power, 2),
            "indice_picco": max_index,
            "timestamp_picco": datetime.fromtimestamp(max_timestamp).isoformat(),
            "offset_ms_dalla_caduta": offset_ms,
            "timestamp_inizio_ascolto": self.start_time,
            "timestamp_fine_ascolto": self.power_readings[-1]['timestamp'],
            "durata_totale_ms": durata_ms,
            "tutti_i_dati": self.power_readings
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Restituisce lo stato del monitoraggio"""
        return {
            "is_monitoring": self.is_monitoring,
            "letture_raccolte": len(self.power_readings),
            "durata_s": round((time.time() - self.start_time), 2) if self.is_monitoring else None,
            "configurazione": self.config
        }