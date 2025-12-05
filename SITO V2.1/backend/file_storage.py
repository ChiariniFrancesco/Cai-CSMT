# backend/file_storage.py
"""
Gestione salvataggio dati su file TXT (testing)
Salva i dati combinati in un file JSON umano-leggibile
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FileStorageManager:
    """Manager per salvare dati su file TXT/JSON"""
    
    def __init__(self, storage_dir: str = "./data"):
        """
        Args:
            storage_dir: Directory dove salvare i file
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)  # Crea dir se non esiste
        
        # File di log generale
        self.log_file = self.storage_dir / "combined_data.jsonl"
        
        # File di indice (per accesso rapido)
        self.index_file = self.storage_dir / "index.json"
        
        logger.info(f"📁 Storage directory: {self.storage_dir.absolute()}")
    
    def save_combined_data(
        self,
        data: Dict[str, Any],
        form_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Salva i dati combinati su file
        
        Args:
            data: Dati combinati (MVD2555 + ExternalSource)
            form_data: Dati del form (corda, assicuratore, operatore)
        
        Returns:
            True se successo, False se errore
        """
        try:
            # Crea il record completo
            record = {
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "form_data": form_data
            }
            
            # Salva in JSONL (JSON Lines - una riga per record)
            with open(self.log_file, 'a') as f:
                json.dump(record, f)
                f.write('\n')  # Newline per ogni record
            
            logger.info(f"✅ Dati salvati in: {self.log_file}")
            
            # Aggiorna indice
            self._update_index(record)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio: {e}")
            return False
    
    def _update_index(self, record: Dict[str, Any]):
        """Aggiorna file di indice per accesso rapido"""
        try:
            # Leggi indice esistente
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    index = json.load(f)
            else:
                index = {"records": [], "total": 0}
            
            # Aggiungi nuovo record
            index["records"].append({
                "timestamp": record["timestamp"],
                "operatore": record.get("form_data", {}).get("operatore", "N/A"),
                "corda": record.get("form_data", {}).get("corda", "N/A"),
                "assicuratore": record.get("form_data", {}).get("assicuratore", "N/A"),
            })
            index["total"] = len(index["records"])
            
            # Salva indice aggiornato
            with open(self.index_file, 'w') as f:
                json.dump(index, f, indent=2)
            
        except Exception as e:
            logger.warning(f"⚠️ Errore aggiornamento indice: {e}")
    
    def get_all_records(self) -> list:
        """Legge TUTTI i record salvati"""
        try:
            records = []
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            records.append(json.loads(line))
            return records
        except Exception as e:
            logger.error(f"❌ Errore lettura record: {e}")
            return []
    
    def get_latest_record(self) -> Optional[Dict[str, Any]]:
        """Legge l'ultimo record salvato"""
        records = self.get_all_records()
        return records[-1] if records else None
    
    def clear_all_records(self) -> bool:
        """Cancella TUTTI i record (attenzione!)"""
        try:
            if self.log_file.exists():
                self.log_file.unlink()
            if self.index_file.exists():
                self.index_file.unlink()
            logger.warning("⚠️ Tutti i record sono stati cancellati")
            return True
        except Exception as e:
            logger.error(f"❌ Errore cancellazione: {e}")
            return False
    
    def print_summary(self):
        """Stampa riepilogo dei dati salvati"""
        records = self.get_all_records()
        print(f"\n📊 RIEPILOGO DATI SALVATI")
        print(f"   Totale record: {len(records)}")
        print(f"   File: {self.log_file}")
        print(f"   Indice: {self.index_file}")
        if records:
            print(f"   Ultimo record: {records[-1]['timestamp']}")
