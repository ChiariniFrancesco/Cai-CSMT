"""
backend/api.py - V2.2 CORRETTO
Sensore MVD2555 collegato FISICAMENTE al Raspberry (backend)
Client riceve solo il segnale di caduta
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging
import asyncio

from database import get_db
from models import ConfigurationMemory
from schemas import ConfigurationCreate, ConfigurationResponse, SubmitFormData
from file_storage import FileStorageManager
from external_data_collector import DataAggregator
from sensor_monitor import SensorMonitor 

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["configurations"])

# Istanze globali
file_storage = FileStorageManager(storage_dir="./data")
aggregator = DataAggregator()
sensor_monitor = None  # Istanza globale del monitor sensore

# ==================== GET ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Server is running",
        "file_storage_ready": True,
        "data_file": str(file_storage.log_file),
        "version": "2.2",
        "sensor_monitoring": sensor_monitor.is_monitoring if sensor_monitor else False
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
    V2.2 CORRETTO:
    1. Riceve dati form
    2. Salva in SQLite
    3. Crea preset se richiesto
    4. INIZIO ASCOLTO SENSORE MVD2555 (backend ha sensore collegato!)
    """
    
    logger.info(f"📨 Dati ricevuti da React: {data}")
    
    global sensor_monitor
    
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
    
    # V2.2 CORRETTO: INIZIO ASCOLTO SENSORE MVD2555
    # Il sensore è collegato FISICAMENTE al Raspberry (backend)
    try:
        if sensor_monitor is None:
            sensor_monitor = SensorMonitor()
        
        # Salva configurazione nel monitor
        sensor_monitor.set_config(
            corda=data.corda,
            assicuratore=data.assicuratore,
            operatore=data.operatore
        )
        
        # Inizia ascolto del sensore MVD2555
        sensor_monitor.start_monitoring()
        
        logger.info("🔊 BACKEND INIZIA ASCOLTO SENSORE MVD2555")
        logger.info(f"   Corda: {data.corda}")
        logger.info(f"   Assicuratore: {data.assicuratore}")
        logger.info(f"   Operatore: {data.operatore}")
        
        response["monitoring_status"] = "STARTED"
        response["monitoring_info"] = "Backend ascoltando sensore MVD2555..."
        
    except Exception as e:
        logger.error(f"❌ Errore avvio monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore avvio monitoring sensore: {str(e)}"
        )
    
    return response

@router.post("/stop-monitoring", response_model=dict)
async def stop_monitoring(stop_data: dict):
    """
    V2.2 CORRETTO:
    Operatore preme "HO FATTO LA CADUTA"
    Backend FERMA ascolto e ANALIZZA i dati raccolti dal sensore MVD2555
    """
    
    global sensor_monitor
    
    if sensor_monitor is None or not sensor_monitor.is_monitoring:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Backend non è in ascolto"
        )
    
    logger.info("⛔ OPERATORE DICE: HO FATTO LA CADUTA!")
    
    try:
        # Ferma ascolto sensore
        sensor_data = sensor_monitor.stop_monitoring()
        
        if sensor_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nessun dato sensore raccolto"
            )
        
        logger.info(f"""
        📊 ANALISI CADUTA COMPLETATA:
        ├─ Letture totali: {sensor_data['letture_totali']}
        ├─ Picco massimo: {sensor_data['picco_potenza_N']:.2f} N
        ├─ Timestamp picco: {sensor_data['timestamp_picco']}
        ├─ Offset dalla caduta: {sensor_data['offset_ms_dalla_caduta']}ms
        └─ Durata ascolto: {sensor_data['durata_totale_ms']}ms
        """)
        
        # Prepara record completo
        operatore = stop_data.get('operatore', 'N/A')
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "tipo_evento": "CADUTA",
            "configurazione": {
                "corda": sensor_monitor.config.get('corda'),
                "assicuratore": sensor_monitor.config.get('assicuratore'),
                "operatore": sensor_monitor.config.get('operatore')
            },
            "analisi_caduta": sensor_data
        }
        
        # Salva su file
        success = file_storage.save_caduta_record(record)
        
        if success:
            logger.info("✅ Record caduta salvato su file")
        
        return {
            "status": "success",
            "message": f"Caduta analizzata - Picco: {sensor_data['picco_potenza_N']:.2f}N",
            "timestamp": datetime.now().isoformat(),
            "analisi_caduta": {
                "picco_potenza_N": sensor_data['picco_potenza_N'],
                "timestamp_picco": sensor_data['timestamp_picco'],
                "offset_ms_dalla_caduta": sensor_data['offset_ms_dalla_caduta'],
                "letture_totali": sensor_data['letture_totali'],
                "durata_totale_ms": sensor_data['durata_totale_ms']
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Errore stop monitoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore analisi caduta: {str(e)}"
        )

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