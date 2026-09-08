"""
backend/sensor_monitor.py - V2.2 con protocollo HBM (MVD2555)

Comunica via seriale con un dispositivo che parla protocollo HBM:
- oggi: Arduino con sketch in modalità HBM-compatibile
- domani: amplificatore MVD2555 reale collegato via USB-RS232

Il codice è lo stesso per entrambi. Per passare al dispositivo reale
basta cambiare SERIAL_PORT (e SERIAL_PARITY se diverso).
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
import threading
import time
import serial

logger = logging.getLogger(__name__)

# ==================== CONFIGURAZIONE SERIALE ====================
# Per l'Arduino-simulatore (Windows):
SERIAL_PORT   = "COM3"
# Per l'MVD2555 reale via adattatore USB-RS232 su Raspberry:
# SERIAL_PORT = "/dev/ttyUSB0"

SERIAL_BAUD   = 9600
# Per Arduino-simulatore: PARITY_NONE
# Per MVD2555 reale (RS232): PARITY_EVEN
SERIAL_PARITY = serial.PARITY_NONE
SERIAL_BYTESIZE = 8
SERIAL_STOPBITS = 1

# Caratteri di controllo HBM
HBM_REMOTE_ON  = b"\x12"             # CTRL+R: attiva remote control
HBM_REMOTE_OFF = b"\x01"             # CTRL+A: chiude remote control


def parse_hbm_value(line: str) -> Optional[float]:
    """
    Decodifica una riga in formato HBM, es. '1,234.5' -> 1234.5.
    La virgola HBM è il separatore delle migliaia, NON il decimale.
    Ritorna None se la riga non è un numero valido.
    """
    s = line.strip().replace(",", "")
    if not s or s in ("0", "?"):
        # 0 = ack di un setting command, ? = errore HBM: ignoriamo
        if s == "0" or s == "?":
            return None
    try:
        return float(s)
    except ValueError:
        return None


class SensorMonitor:
    """
    Monitora un sensore HBM (Arduino-sim o MVD2555) collegato via seriale.

    FLUSSO:
      set_config() -> salva i dati del form
      start_monitoring() -> apre seriale, attiva remote, avvia streaming
      _read_loop in background accumula letture
      stop_monitoring() -> ferma streaming, chiude remote, analizza picco
    """

    def __init__(self):
        self.is_monitoring = False
        self.power_readings: list = []
        self.start_time: Optional[float] = None
        self.config: Dict[str, Any] = {}
        self.monitoring_thread: Optional[threading.Thread] = None
        self.serial_conn: Optional[serial.Serial] = None

    def set_config(self, corda: str, assicuratore: str, operatore: str):
        self.config = {
            "corda": corda,
            "assicuratore": assicuratore,
            "operatore": operatore
        }
        logger.info(f"📋 Configurazione set: {self.config}")

    def start_monitoring(self):
        """Apre seriale, manda sequenza HBM, avvia thread di lettura."""
        if self.is_monitoring:
            logger.warning("⚠️ Monitoraggio già in corso")
            return

        # --- 1. Apertura porta seriale ---
        try:
            self.serial_conn = serial.Serial(
                port=SERIAL_PORT,
                baudrate=SERIAL_BAUD,
                parity=SERIAL_PARITY,
                bytesize=SERIAL_BYTESIZE,
                stopbits=SERIAL_STOPBITS,
                timeout=2
            )
            # Arduino si resetta all'apertura della seriale (l'MVD2555 no).
            # Aspettiamo per sicurezza, poi puliamo il buffer.
            time.sleep(2)
            self.serial_conn.reset_input_buffer()
            logger.info(f"🔌 Seriale aperta su {SERIAL_PORT} (parity={SERIAL_PARITY})")
        except serial.SerialException as e:
            logger.error(f"❌ Impossibile aprire la seriale: {e}")
            self.serial_conn = None
            raise

        # --- 2. Sequenza di avvio HBM ---
        try:
            # Attiva remote control
            self.serial_conn.write(HBM_REMOTE_ON)
            time.sleep(0.05)

            # Imposta output ASCII semplice (solo valore)
            self.serial_conn.write(b"COF1\r\n")
            time.sleep(0.05)
            self._consume_ack("COF1")

            # Cancella picchi memorizzati nel sensore (se ce ne fossero)
            self.serial_conn.write(b"CPV\r\n")
            time.sleep(0.05)
            self._consume_ack("CPV")

            # Tara: azzera la baseline. Importante con cella di carico vera.
            self.serial_conn.write(b"TAR\r\n")
            time.sleep(0.1)
            self._consume_ack("TAR")

            # Avvia streaming infinito del valore gross
            self.serial_conn.write(b"MSV?1,0\r\n")
            logger.info("➡️ Sequenza HBM inviata: CTRL+R, COF1, CPV, TAR, MSV?1,0")

        except Exception as e:
            logger.error(f"❌ Errore invio sequenza HBM: {e}")
            try:
                self.serial_conn.close()
            except Exception:
                pass
            self.serial_conn = None
            raise

        # --- 3. Avvia thread di lettura ---
        self.is_monitoring = True
        self.power_readings = []
        self.start_time = time.time()

        logger.info(f"""
        🔊 ===============================
        🔊 INIZIO ASCOLTO SENSORE HBM
        🔊 ===============================
        🔊 Timestamp: {datetime.now().isoformat()}
        🔊 Corda:     {self.config.get('corda')}
        🔊 Assicuratore: {self.config.get('assicuratore')}
        🔊 Operatore: {self.config.get('operatore')}
        🔊 ===============================
        """)

        self.monitoring_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.monitoring_thread.start()

    def _consume_ack(self, cmd_name: str):
        """Legge l'ack 0/? di un setting command e lo logga."""
        try:
            ack = self.serial_conn.readline().decode("ascii", errors="ignore").strip()
            if ack == "0":
                logger.debug(f"✅ ACK {cmd_name}: OK")
            elif ack == "?":
                logger.warning(f"⚠️ ACK {cmd_name}: ERROR")
            elif ack:
                logger.debug(f"   ACK {cmd_name}: '{ack}'")
        except Exception as e:
            logger.debug(f"   (no ACK ricevuto per {cmd_name}: {e})")

    def _read_loop(self):
        """
        Legge in continuo dalla seriale finché is_monitoring resta True.
        Ogni riga ricevuta viene parsata come valore HBM (es. '1,234.5').
        """
        logger.info("🔄 Loop di lettura avviato")
        while self.is_monitoring:
            try:
                raw = self.serial_conn.readline()
                if not raw:
                    continue
                line = raw.decode("ascii", errors="ignore").strip()
                if not line:
                    continue

                value = parse_hbm_value(line)
                if value is not None:
                    self._add_reading(value)

            except serial.SerialException as e:
                logger.error(f"❌ Errore seriale: {e}")
                break
            except Exception as e:
                logger.error(f"❌ Errore loop: {e}")
                break

        logger.info(f"🛑 Loop terminato. Letture: {len(self.power_readings)}")

    def _add_reading(self, power: float):
        if not self.is_monitoring:
            return
        self.power_readings.append({
            "timestamp": time.time(),
            "value": round(power, 2)
        })

    def stop_monitoring(self) -> Optional[Dict[str, Any]]:
        """Ferma lo streaming HBM, chiude la seriale, analizza i dati."""
        if not self.is_monitoring:
            logger.warning("⚠️ Monitoraggio non in corso")
            return None

        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=3)

        # Sequenza di chiusura HBM
        if self.serial_conn:
            try:
                self.serial_conn.write(b"STP\r\n")
                time.sleep(0.1)
                self.serial_conn.write(HBM_REMOTE_OFF)
                logger.info("➡️ Inviati STP + CTRL+A (chiude remote)")
                time.sleep(0.1)
            except Exception as e:
                logger.warning(f"⚠️ Errore in sequenza di stop: {e}")
            finally:
                try:
                    self.serial_conn.close()
                    logger.info("🔌 Seriale chiusa")
                except Exception:
                    pass
                self.serial_conn = None

        logger.info(f"⛔ FINE ASCOLTO. Letture totali: {len(self.power_readings)}")

        if len(self.power_readings) == 0:
            logger.warning("⚠️ Nessun dato raccolto")
            return None

        # Calcolo del picco e degli offset
        max_power = 0.0
        max_index = 0
        max_timestamp = self.power_readings[0]["timestamp"]
        for i, r in enumerate(self.power_readings):
            if r["value"] > max_power:
                max_power = r["value"]
                max_index = i
                max_timestamp = r["timestamp"]

        offset_ms = int((max_timestamp - self.start_time) * 1000)
        durata_ms = int((self.power_readings[-1]["timestamp"] - self.start_time) * 1000)

        logger.info(f"""
        📊 ANALISI:
        ├─ Letture: {len(self.power_readings)}
        ├─ Picco: {max_power:.2f}
        ├─ Indice picco: {max_index}
        ├─ Offset dalla caduta: {offset_ms}ms
        └─ Durata: {durata_ms}ms
        """)

        return {
            "letture_totali": len(self.power_readings),
            "picco_potenza_N": round(max_power, 2),
            "indice_picco": max_index,
            "timestamp_picco": datetime.fromtimestamp(max_timestamp).isoformat(),
            "offset_ms_dalla_caduta": offset_ms,
            "timestamp_inizio_ascolto": self.start_time,
            "timestamp_fine_ascolto": self.power_readings[-1]["timestamp"],
            "durata_totale_ms": durata_ms,
            "tutti_i_dati": self.power_readings
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_monitoring": self.is_monitoring,
            "letture_raccolte": len(self.power_readings),
            "durata_s": round((time.time() - self.start_time), 2) if self.is_monitoring else None,
            "configurazione": self.config,
            "serial_port": SERIAL_PORT,
            "protocol": "HBM Interpreter (MVD2555-compatible)"
        }