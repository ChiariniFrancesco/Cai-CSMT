# backend/api.py
"""
API endpoints - Fase 1 + 2 con File Storage
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging

from database import get_db
from models import ConfigurationMemory
from schemas import ConfigurationCreate, ConfigurationResponse, SubmitFormData
from file_storage import FileStorageManager
from external_data_collector import DataAggregator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["configurations"])

# Istanze globali
file_storage = FileStorageManager(storage_dir="./data")
aggregator = DataAggregator()

# ==================== GET ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Server is running",
        "file_storage_ready": True,
        "data_file": str(file_storage.log_file)
    }

@router.get("/configurations", response_model=List[ConfigurationResponse])
async def get_all_configurations(db: Session = Depends(get_db)):
    """Ottieni TUTTE le configurazioni salvate"""
    configurations = db.query(ConfigurationMemory).all()
    return configurations

@router.get("/configurations/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(config_id: int, db: Session = Depends(get_db)):
    """Ottieni UNA configurazione specifica"""
    config = db.query(ConfigurationMemory).filter(
        ConfigurationMemory.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configurazione {config_id} non trovata"
        )
    
    return config

@router.get("/data/records")
async def get_all_records():
    """Leggi TUTTI i record salvati"""
    records = file_storage.get_all_records()
    return {"total": len(records), "records": records}

@router.get("/data/latest")
async def get_latest_record():
    """Leggi l'ultimo record salvato"""
    record = file_storage.get_latest_record()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessun record salvato"
        )
    return record

# ==================== POST ====================

@router.post("/submit", response_model=dict)
async def submit_form(
    data: SubmitFormData,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    FASE 1 + 2 COMBINATE:
    1. Riceve dati form
    2. Salva in SQLite
    3. Crea preset se richiesto
    4. Triggera background task per raccogliere dati + salvare su file
    """
    
    logger.info(f"📨 Dati ricevuti da React: {data}")
    
    # Response iniziale
    response = {
        "status": "success",
        "message": "Dati ricevuti",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "corda": data.corda,
            "assicuratore": data.assicuratore,
            "operatore": data.operatore
        }
    }
    
    # FASE 1: Salva preset se richiesto
    if data.salva_come_preset:
        try:
            existing = db.query(ConfigurationMemory).filter(
                ConfigurationMemory.nome_preset == data.salva_come_preset
            ).first()
            
            if existing:
                existing.corda = data.corda
                existing.assicuratore = data.assicuratore
                existing.operatore = data.operatore
                db.commit()
                response["preset_saved"] = f"Preset '{data.salva_come_preset}' aggiornato"
            else:
                new_config = ConfigurationMemory(
                    nome_preset=data.salva_come_preset,
                    corda=data.corda,
                    assicuratore=data.assicuratore,
                    operatore=data.operatore
                )
                db.add(new_config)
                db.commit()
                response["preset_saved"] = f"Preset '{data.salva_come_preset}' creato"
        
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Errore nel salvare preset: {str(e)}"
            )
    
    # FASE 2: Triggera raccolta dati + salvataggio file in background
    if background_tasks:
        background_tasks.add_task(
            collect_and_save_to_file,
            form_data=data
        )
        response["background_task"] = "Raccolta dati e salvataggio file in corso..."
    
    return response

# ==================== BACKGROUND TASK ====================

async def collect_and_save_to_file(form_data: SubmitFormData):
    """
    Background task che:
    1. Raccoglie dati da MVD2555
    2. Raccoglie dati da fonte esterna
    3. Li combina con i dati del form
    4. Li salva su file TXT
    """
    try:
        logger.info("🔄 Background task: inizio raccolta dati...")
        
        # Raccoglie dati combinati da entrambe le sorgenti
        combined_data = await aggregator.get_combined_data()
        
        if combined_data is None:
            logger.warning("⚠️ Dati combinati non disponibili")
            return
        
        # Prepara dati del form
        form_dict = {
            "corda": form_data.corda,
            "assicuratore": form_data.assicuratore,
            "operatore": form_data.operatore,
            "salva_come_preset": form_data.salva_come_preset
        }
        
        # Salva su file
        success = file_storage.save_combined_data(
            data=combined_data,
            form_data=form_dict
        )
        
        if success:
            logger.info(f"✅ Dati salvati su file: {file_storage.log_file}")
        else:
            logger.error("❌ Errore salvataggio file")
    
    except Exception as e:
        logger.error(f"❌ Errore background task: {e}")

# ==================== DELETE ====================

@router.delete("/configurations/{config_id}")
async def delete_configuration(config_id: int, db: Session = Depends(get_db)):
    """Elimina una configurazione salvata"""
    config = db.query(ConfigurationMemory).filter(
        ConfigurationMemory.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configurazione {config_id} non trovata"
        )
    
    db.delete(config)
    db.commit()
    
    return {"status": "success", "message": f"Configurazione {config_id} eliminata"}

@router.delete("/data/clear")
async def clear_all_data():
    """ATTENZIONE: Cancella TUTTI i record salvati"""
    success = file_storage.clear_all_records()
    if success:
        return {"status": "success", "message": "Tutti i record sono stati cancellati"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore cancellazione record"
        )
