"""
backend/sensor_monitor.py - V2.2 CORRETTO
Monitor per ascolto CONTINUO del sensore MVD2555 collegato al Raspberry
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import random

logger = logging.getLogger(__name__)

class SensorMonitor:
    """
    Monitora il sensore MVD2555 collegato fisicamente al Raspberry
    
    FLUSSO:
    1. CONFERMA form → start_monitoring()
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
        self.monitoring_task = None
        
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
        
        Il sensore è collegato al Raspberry via seriale
        Legge dati continuamente ogni 2ms circa
        """
        if self.is_monitoring:
            logger.warning("⚠️ Monitoraggio già in corso")
            return
        
        self.is_monitoring = True
        self.power_readings = []
        self.start_time = datetime.now().timestamp()
        
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
        
        # Avvia thread di lettura sensore
        # In realtà questo avviene in background continuamente
        # Nel nostro test simuleremo con dati fake
    
    def read_sensor(self) -> float:
        """
        Legge un valore dal sensore MVD2555
        
        REALE: legge da seriale (pyserial)
        TEST: genera dati fake con picchi casuali
        """
        
        # SIMULAZIONE per testing
        # In produzione: leggi da pyserial
        
        # Baseline potenza (20-70 N)
        basePower = random.random() * 50 + 20
        
        # Rumore casuale
        noisePower = basePower + (random.random() * 100 - 50)
        
        # Assicura range 0-500
        power = max(0, min(500, noisePower))
        
        return power
    
    def add_reading(self, power: float):
        """Aggiunge una lettura al record"""
        if not self.is_monitoring:
            return
        
        reading = {
            "timestamp": datetime.now().timestamp(),
            "value": round(power, 2)
        }
        
        self.power_readings.append(reading)
    
    def stop_monitoring(self) -> Optional[Dict[str, Any]]:
        """
        FINE ASCOLTO sensore
        Operatore ha premuto "HO FATTO LA CADUTA"
        
        Analizza i dati raccolti e trova il picco
        """
        
        if not self.is_monitoring:
            logger.warning("⚠️ Monitoraggio non in corso")
            return None
        
        self.is_monitoring = False
        
        logger.info(f"""
        ⛔ ===============================
        ⛔ FINE ASCOLTO SENSORE MVD2555
        ⛔ ===============================
        ⛔ Timestamp fine: {datetime.now().isoformat()}
        ⛔ Letture totali: {len(self.power_readings)}
        ⛔ ===============================
        """)
        
        # Analizza dati raccolti
        if len(self.power_readings) == 0:
            logger.warning("⚠️ Nessun dato raccolto dal sensore")
            return None
        
        # SIMULAZIONE: generiamo dati fake
        # In produzione, analizzeremmo i dati reali raccolti
        self._simulate_sensor_data()
        
        # Trova il picco massimo
        max_power = 0
        max_index = 0
        max_timestamp = None
        
        for i, reading in enumerate(self.power_readings):
            if reading['value'] > max_power:
                max_power = reading['value']
                max_index = i
                max_timestamp = reading['timestamp']
        
        # Calcola offset
        offset_ms = int((max_timestamp - self.start_time) * 1000)
        
        logger.info(f"""
        📊 ANALISI COMPLETATA:
        ├─ Letture totali: {len(self.power_readings)}
        ├─ Picco massimo: {max_power:.2f} N
        ├─ Indice picco: {max_index}
        ├─ Timestamp picco: {datetime.fromtimestamp(max_timestamp).isoformat()}
        ├─ Offset dalla caduta: {offset_ms}ms
        ├─ Durata ascolto: {int((self.power_readings[-1]['timestamp'] - self.start_time) * 1000)}ms
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
            "durata_totale_ms": int((self.power_readings[-1]['timestamp'] - self.start_time) * 1000),
            "tutti_i_dati": self.power_readings
        }
    
    def _simulate_sensor_data(self):
        """
        SIMULAZIONE: genera dati fake realistici
        
        In produzione, i dati arrivano dal sensore MVD2555 reale
        Questo metodo simula il sensore per testing
        """
        
        # Se non abbiamo ancora dati, generali
        if len(self.power_readings) < 100:
            # Genera ~100-200 letture
            num_readings = random.randint(100, 200)
            
            for i in range(num_readings):
                # Baseline
                base = 30 + (random.random() * 40)
                
                # Aggiungi picco nel mezzo (simulando la caduta)
                if 30 < i < 80:  # Picco intorno al 50-60% del tempo
                    # Aumenta verso il picco
                    progress = (i - 30) / 50
                    peak_height = 350 + (random.random() * 100)
                    power = base + (peak_height * progress)
                else:
                    power = base
                
                self.power_readings.append({
                    "timestamp": self.start_time + (i * 0.002),  # 2ms intervallo
                    "value": round(max(0, min(500, power)), 2)
                })
    
    def get_status(self) -> Dict[str, Any]:
        """Restituisce lo stato del monitoraggio"""
        return {
            "is_monitoring": self.is_monitoring,
            "letture_raccolte": len(self.power_readings),
            "durata_s": round((datetime.now().timestamp() - self.start_time), 2) if self.is_monitoring else None,
            "configurazione": self.config
        }