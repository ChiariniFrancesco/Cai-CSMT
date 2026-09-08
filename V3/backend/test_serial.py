"""Mini-test isolato del SensorMonitor — non passa per FastAPI"""
import logging
import time
from sensor_monitor import SensorMonitor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

monitor = SensorMonitor()
monitor.set_config(corda="test_corda", assicuratore="test_ass", operatore="test_op")

print("Avvio monitoraggio...")
monitor.start_monitoring()

# Lascia che la rampa Arduino completi (dura ~6.5s)
time.sleep(8)

print("Stop monitoraggio e analisi...")
result = monitor.stop_monitoring()

print("\n========== RISULTATO ==========")
print(f"Letture totali: {result['letture_totali']}")
print(f"Picco: {result['picco_potenza_N']}")
print(f"Offset picco: {result['offset_ms_dalla_caduta']}ms")
print(f"Durata: {result['durata_totale_ms']}ms")