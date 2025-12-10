"""
backend/file_storage.py - V2.2 CORRETTO
Gestione file storage per:
- combined_data.jsonl (V2.1 - configurazioni)
- cadute_data.jsonl (V2.2 - cadute)
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class FileStorageManager:
    """Gestisce il salvataggio dei dati su file JSONL"""
    
    def __init__(self, storage_dir: str = "./data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # File per configurazioni (V2.1)
        self.combined_file = self.storage_dir / "combined_data.jsonl"
        
        # File per cadute (V2.2 NUOVO)
        self.cadute_file = self.storage_dir / "cadute_data.jsonl"
        
        # Indice
        self.index_file = self.storage_dir / "index.json"
        self.log_file = self.combined_file
        
        logger.info(f"📁 Storage directory: {self.storage_dir}")
        logger.info(f"📄 Combined data file: {self.combined_file}")
        logger.info(f"⛔ Cadute data file: {self.cadute_file}")
        
        self._init_index()
    
    def _init_index(self):
        """Inizializza l'indice se non esiste"""
        if not self.index_file.exists():
            index = {
                "total_configurations": 0,
                "total_cadute": 0,
                "last_updated": datetime.now().isoformat(),
                "version": "2.2"
            }
            self._save_index(index)
    
    def _load_index(self) -> Dict[str, Any]:
        """Carica l'indice"""
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
        """Salva l'indice"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Errore salvataggio indice: {e}")
    
    # ==================== CONFIGURAZIONI (V2.1) ====================
    
    def save_combined_data(self, data: Dict[str, Any], form_data: Dict[str, Any]) -> bool:
        """Salva dati combinati (configurazioni V2.1)"""
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
    
    # ==================== CADUTE (V2.2 NUOVO) ====================
    
    def save_caduta_record(self, record: Dict[str, Any]) -> bool:
        """
        Salva un record di caduta su cadute_data.jsonl
        
        Record contiene:
        - timestamp
        - tipo_evento: "CADUTA"
        - configurazione (corda, assicuratore, operatore)
        - analisi_caduta (picco, offset, dati sensore)
        """
        try:
            with open(self.cadute_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            logger.info(f"✅ Record caduta salvato su {self.cadute_file}")
            
            # Aggiorna indice
            self._update_caduta_index()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio caduta: {e}")
            return False
    
    def _update_caduta_index(self):
        """Aggiorna il conteggio cadute nell'indice"""
        try:
            index = self._load_index()
            
            # Conta le cadute nel file
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
    
    def get_all_cadute(self) -> List[Dict[str, Any]]:
        """Legge TUTTE le cadute dal file"""
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
        """Legge l'ULTIMA caduta dal file"""
        try:
            if self.cadute_file.exists():
                with open(self.cadute_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        return json.loads(lines[-1])
        except Exception as e:
            logger.error(f"❌ Errore lettura ultima caduta: {e}")
        
        return None
    
    # ==================== RECORDS (V2.1) ====================
    
    def get_all_records(self) -> List[Dict[str, Any]]:
        """Legge TUTTI i record dal file"""
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
        """Legge l'ULTIMO record dal file"""
        try:
            if self.combined_file.exists():
                with open(self.combined_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        return json.loads(lines[-1])
        except Exception as e:
            logger.error(f"❌ Errore lettura ultimo record: {e}")
        
        return None
    
    # ==================== UTILITY ====================
    
    def clear_all_records(self) -> bool:
        """Cancella TUTTI i record (ATTENZIONE!)"""
        try:
            if self.combined_file.exists():
                self.combined_file.unlink()
            if self.cadute_file.exists():
                self.cadute_file.unlink()
            
            self._init_index()
            logger.info("✅ Tutti i record cancellati")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore cancellazione record: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Restituisce lo stato dello storage"""
        index = self._load_index()
        
        combined_exists = self.combined_file.exists()
        cadute_exists = self.cadute_file.exists()
        
        combined_size = self.combined_file.stat().st_size if combined_exists else 0
        cadute_size = self.cadute_file.stat().st_size if cadute_exists else 0
        
        return {
            "storage_dir": str(self.storage_dir),
            "combined_file": str(self.combined_file),
            "combined_size_bytes": combined_size,
            "cadute_file": str(self.cadute_file),
            "cadute_size_bytes": cadute_size,
            "index": index
        }

# # backend/file_storage.py
# """
# Gestione salvataggio dati su file TXT (testing)
# Salva i dati combinati in un file JSON umano-leggibile
# """

# import json
# import logging
# from datetime import datetime
# from pathlib import Path
# from typing import Dict, Any, Optional

# logger = logging.getLogger(__name__)

# class FileStorageManager:
#     """Manager per salvare dati su file TXT/JSON"""
    
#     def __init__(self, storage_dir: str = "./data"):
#         """
#         Args:
#             storage_dir: Directory dove salvare i file
#         """
#         self.storage_dir = Path(storage_dir)
#         self.storage_dir.mkdir(exist_ok=True)  # Crea dir se non esiste
        
#         # File di log generale
#         self.log_file = self.storage_dir / "combined_data.jsonl"
        
#         # File di indice (per accesso rapido)
#         self.index_file = self.storage_dir / "index.json"
        
#         logger.info(f"📁 Storage directory: {self.storage_dir.absolute()}")
    
#     def save_combined_data(
#         self,
#         data: Dict[str, Any],
#         form_data: Optional[Dict[str, Any]] = None
#     ) -> bool:
#         """
#         Salva i dati combinati su file
        
#         Args:
#             data: Dati combinati (MVD2555 + ExternalSource)
#             form_data: Dati del form (corda, assicuratore, operatore)
        
#         Returns:
#             True se successo, False se errore
#         """
#         try:
#             # Crea il record completo
#             record = {
#                 "timestamp": datetime.now().isoformat(),
#                 "data": data,
#                 "form_data": form_data
#             }
            
#             # Salva in JSONL (JSON Lines - una riga per record)
#             with open(self.log_file, 'a') as f:
#                 json.dump(record, f)
#                 f.write('\n')  # Newline per ogni record
            
#             logger.info(f"✅ Dati salvati in: {self.log_file}")
            
#             # Aggiorna indice
#             self._update_index(record)
            
#             return True
            
#         except Exception as e:
#             logger.error(f"❌ Errore salvataggio: {e}")
#             return False
    
#     def _update_index(self, record: Dict[str, Any]):
#         """Aggiorna file di indice per accesso rapido"""
#         try:
#             # Leggi indice esistente
#             if self.index_file.exists():
#                 with open(self.index_file, 'r') as f:
#                     index = json.load(f)
#             else:
#                 index = {"records": [], "total": 0}
            
#             # Aggiungi nuovo record
#             index["records"].append({
#                 "timestamp": record["timestamp"],
#                 "operatore": record.get("form_data", {}).get("operatore", "N/A"),
#                 "corda": record.get("form_data", {}).get("corda", "N/A"),
#                 "assicuratore": record.get("form_data", {}).get("assicuratore", "N/A"),
#             })
#             index["total"] = len(index["records"])
            
#             # Salva indice aggiornato
#             with open(self.index_file, 'w') as f:
#                 json.dump(index, f, indent=2)
            
#         except Exception as e:
#             logger.warning(f"⚠️ Errore aggiornamento indice: {e}")
    
#     def get_all_records(self) -> list:
#         """Legge TUTTI i record salvati"""
#         try:
#             records = []
#             if self.log_file.exists():
#                 with open(self.log_file, 'r') as f:
#                     for line in f:
#                         if line.strip():
#                             records.append(json.loads(line))
#             return records
#         except Exception as e:
#             logger.error(f"❌ Errore lettura record: {e}")
#             return []
    
#     def get_latest_record(self) -> Optional[Dict[str, Any]]:
#         """Legge l'ultimo record salvato"""
#         records = self.get_all_records()
#         return records[-1] if records else None
    
#     def clear_all_records(self) -> bool:
#         """Cancella TUTTI i record (attenzione!)"""
#         try:
#             if self.log_file.exists():
#                 self.log_file.unlink()
#             if self.index_file.exists():
#                 self.index_file.unlink()
#             logger.warning("⚠️ Tutti i record sono stati cancellati")
#             return True
#         except Exception as e:
#             logger.error(f"❌ Errore cancellazione: {e}")
#             return False
    
#     def print_summary(self):
#         """Stampa riepilogo dei dati salvati"""
#         records = self.get_all_records()
#         print(f"\n📊 RIEPILOGO DATI SALVATI")
#         print(f"   Totale record: {len(records)}")
#         print(f"   File: {self.log_file}")
#         print(f"   Indice: {self.index_file}")
#         if records:
#             print(f"   Ultimo record: {records[-1]['timestamp']}")
