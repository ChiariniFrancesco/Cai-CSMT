"""
backend/file_storage.py - V2.2 con CSV "vivi" + export on-demand
- combined_data.jsonl (V2.1, legacy)
- cadute_data.jsonl (V2.2, archivio completo in JSON)
- cadute_summary.csv  (V2.2, si aggiorna ad ogni caduta — riassunto)
- cadute_timeseries.csv (V2.2, si aggiorna ad ogni caduta — tutte le serie)
"""

import json
import logging
import io
import csv
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class FileStorageManager:
    """Gestisce il salvataggio dei dati su file JSONL + CSV"""
    
    def __init__(self, storage_dir: str = "./data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # File JSONL legacy V2.1
        self.combined_file = self.storage_dir / "combined_data.jsonl"
        
        # File JSONL V2.2 (archivio completo)
        self.cadute_file = self.storage_dir / "cadute_data.jsonl"
        
        # CSV "vivi" che si aggiornano automaticamente ad ogni caduta
        self.cadute_summary_csv = self.storage_dir / "cadute_summary.csv"
        self.cadute_timeseries_csv = self.storage_dir / "cadute_timeseries.csv"
        
        # Indice
        self.index_file = self.storage_dir / "index.json"
        self.log_file = self.combined_file
        
        logger.info(f"📁 Storage directory: {self.storage_dir}")
        logger.info(f"📄 Cadute JSONL: {self.cadute_file}")
        logger.info(f"📊 CSV summary: {self.cadute_summary_csv}")
        logger.info(f"📊 CSV timeseries: {self.cadute_timeseries_csv}")
        
        self._init_index()
    
    def _init_index(self):
        if not self.index_file.exists():
            index = {
                "total_configurations": 0,
                "total_cadute": 0,
                "last_updated": datetime.now().isoformat(),
                "version": "2.2"
            }
            self._save_index(index)
    
    def _load_index(self) -> Dict[str, Any]:
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ Errore caricamento indice: {e}")
        return {
            "total_configurations": 0,
            "total_cadute": 0,
            "last_updated": datetime.now().isoformat(),
            "version": "2.2"
        }
    
    def _save_index(self, index: Dict[str, Any]):
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Errore salvataggio indice: {e}")
    
    # ==================== LEGACY V2.1 ====================
    
    def save_combined_data(self, data: Dict[str, Any], form_data: Dict[str, Any]) -> bool:
        try:
            record = {
                "timestamp": datetime.now().isoformat(),
                "tipo_evento": "CONFIGURAZIONE",
                "form": form_data,
                "dati_sensori": data
            }
            with open(self.combined_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            logger.info(f"✅ Dati combinati salvati su {self.combined_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Errore salvataggio dati combinati: {e}")
            return False
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        records = []
        try:
            if self.combined_file.exists():
                with open(self.combined_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            records.append(json.loads(line))
        except Exception as e:
            logger.error(f"❌ Errore lettura record: {e}")
        return records
    
    def get_latest_record(self) -> Optional[Dict[str, Any]]:
        try:
            if self.combined_file.exists():
                with open(self.combined_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        return json.loads(lines[-1])
        except Exception as e:
            logger.error(f"❌ Errore lettura ultimo record: {e}")
        return None
    
    # ==================== CADUTE V2.2 ====================
    
    def save_caduta_record(self, record: Dict[str, Any]) -> bool:
        """
        Salva la caduta su:
        - JSONL (archivio completo)
        - CSV summary (1 riga per caduta)
        - CSV timeseries (N righe per caduta, N = letture)
        """
        try:
            # JSONL
            with open(self.cadute_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            logger.info(f"✅ Record caduta salvato su {self.cadute_file}")
            self._update_caduta_index()
            
            # CSV "vivi"
            self._append_to_summary_csv(record)
            self._append_to_timeseries_csv(record)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio caduta: {e}")
            return False
    
    def _update_caduta_index(self):
        try:
            index = self._load_index()
            cadute_count = 0
            if self.cadute_file.exists():
                with open(self.cadute_file, 'r', encoding='utf-8') as f:
                    cadute_count = sum(1 for _ in f)
            index["total_cadute"] = cadute_count
            index["last_updated"] = datetime.now().isoformat()
            self._save_index(index)
            logger.info(f"📊 Indice aggiornato: {cadute_count} cadute")
        except Exception as e:
            logger.error(f"❌ Errore aggiornamento indice: {e}")
    
    def _append_to_summary_csv(self, record: Dict[str, Any]):
        """Appende UNA riga al CSV di riassunto. Crea l'header se serve."""
        try:
            file_exists = self.cadute_summary_csv.exists() and self.cadute_summary_csv.stat().st_size > 0
            
            with open(self.cadute_summary_csv, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                
                if not file_exists:
                    writer.writerow([
                        "timestamp", "corda", "assicuratore", "operatore",
                        "picco_N", "offset_ms", "durata_ms", "letture_totali"
                    ])
                
                config = record.get("configurazione", {})
                analisi = record.get("analisi_caduta", {})
                writer.writerow([
                    record.get("timestamp", ""),
                    config.get("corda", ""),
                    config.get("assicuratore", ""),
                    config.get("operatore", ""),
                    analisi.get("picco_potenza_N", ""),
                    analisi.get("offset_ms_dalla_caduta", ""),
                    analisi.get("durata_totale_ms", ""),
                    analisi.get("letture_totali", ""),
                ])
            logger.info(f"📊 Riga appesa a {self.cadute_summary_csv}")
        except Exception as e:
            logger.error(f"❌ Errore append summary CSV: {e}")
    
    def _append_to_timeseries_csv(self, record: Dict[str, Any]):
        """Appende le righe della serie temporale di una caduta. Crea l'header se serve."""
        try:
            file_exists = self.cadute_timeseries_csv.exists() and self.cadute_timeseries_csv.stat().st_size > 0
            
            with open(self.cadute_timeseries_csv, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                
                if not file_exists:
                    writer.writerow([
                        "caduta_id", "operatore", "indice",
                        "timestamp_unix", "offset_ms_da_inizio", "value_N"
                    ])
                
                caduta_id = record.get("timestamp", "")
                config = record.get("configurazione", {})
                operatore = config.get("operatore", "")
                analisi = record.get("analisi_caduta", {})
                dati = analisi.get("tutti_i_dati", [])
                start_time = analisi.get("timestamp_inizio_ascolto")
                
                for i, punto in enumerate(dati):
                    t = punto.get("timestamp", 0)
                    v = punto.get("value", 0)
                    offset_ms = int((t - start_time) * 1000) if start_time else ""
                    writer.writerow([caduta_id, operatore, i, t, offset_ms, v])
            
            logger.info(f"📊 Serie temporale appesa a {self.cadute_timeseries_csv}")
        except Exception as e:
            logger.error(f"❌ Errore append timeseries CSV: {e}")
    
    def get_all_cadute(self) -> List[Dict[str, Any]]:
        cadute = []
        try:
            if self.cadute_file.exists():
                with open(self.cadute_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            cadute.append(json.loads(line))
        except Exception as e:
            logger.error(f"❌ Errore lettura cadute: {e}")
        return cadute
    
    def get_latest_caduta(self) -> Optional[Dict[str, Any]]:
        try:
            if self.cadute_file.exists():
                with open(self.cadute_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        return json.loads(lines[-1])
        except Exception as e:
            logger.error(f"❌ Errore lettura ultima caduta: {e}")
        return None
    
    # ==================== EXPORT CSV (download via API) ====================
    
    def export_cadute_summary_csv(self) -> str:
        """Riassunto: una riga per caduta. Stringa CSV."""
        cadute = self.get_all_cadute()
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow([
            "timestamp", "corda", "assicuratore", "operatore",
            "picco_N", "offset_ms", "durata_ms", "letture_totali"
        ])
        for c in cadute:
            config = c.get("configurazione", {})
            analisi = c.get("analisi_caduta", {})
            writer.writerow([
                c.get("timestamp", ""),
                config.get("corda", ""),
                config.get("assicuratore", ""),
                config.get("operatore", ""),
                analisi.get("picco_potenza_N", ""),
                analisi.get("offset_ms_dalla_caduta", ""),
                analisi.get("durata_totale_ms", ""),
                analisi.get("letture_totali", ""),
            ])
        return output.getvalue()
    
    def export_caduta_timeseries_csv(self, index: int) -> Optional[str]:
        """Serie temporale di UNA caduta. index 0 = prima, -1 = ultima."""
        cadute = self.get_all_cadute()
        if not cadute:
            return None
        try:
            caduta = cadute[index]
        except IndexError:
            return None
        analisi = caduta.get("analisi_caduta", {})
        dati = analisi.get("tutti_i_dati", [])
        start_time = analisi.get("timestamp_inizio_ascolto")
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(["indice", "timestamp_unix", "offset_ms_da_inizio", "value_N"])
        for i, punto in enumerate(dati):
            t = punto.get("timestamp", 0)
            v = punto.get("value", 0)
            offset_ms = int((t - start_time) * 1000) if start_time else ""
            writer.writerow([i, t, offset_ms, v])
        return output.getvalue()
    
    # ==================== UTILITY ====================
    
    def clear_all_records(self) -> bool:
        """Cancella TUTTI i record (JSONL + CSV)"""
        try:
            for f in [self.combined_file, self.cadute_file,
                      self.cadute_summary_csv, self.cadute_timeseries_csv]:
                if f.exists():
                    f.unlink()
            self._init_index()
            logger.info("✅ Tutti i record cancellati")
            return True
        except Exception as e:
            logger.error(f"❌ Errore cancellazione record: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        index = self._load_index()
        return {
            "storage_dir": str(self.storage_dir),
            "cadute_jsonl": str(self.cadute_file),
            "cadute_summary_csv": str(self.cadute_summary_csv),
            "cadute_timeseries_csv": str(self.cadute_timeseries_csv),
            "index": index
        }