"""
backend/api.py - V2.2 con export CSV
Sensore (Arduino simulatore o futuro MVD2555) collegato fisicamente al backend via USB.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging

from database import get_db
from models import ConfigurationMemory
from schemas import ConfigurationCreate, ConfigurationResponse, SubmitFormData
from file_storage import FileStorageManager
from sensor_monitor import SensorMonitor 

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["configurations"])

# Istanze globali
file_storage = FileStorageManager(storage_dir="./data")
sensor_monitor = None                 # creato al primo POST /submit

# ==================== GET ====================

@router.get("/health")
async def health_check():
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
    return db.query(ConfigurationMemory).all()

@router.get("/configurations/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(config_id: int, db: Session = Depends(get_db)):
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
    records = file_storage.get_all_records()
    return {"total": len(records), "records": records}

@router.get("/data/latest")
async def get_latest_record():
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
    Riceve i dati del form, salva preset (se richiesto),
    avvia ascolto sensore (apre seriale Arduino + thread di lettura).
    """
    logger.info(f"📨 Dati ricevuti da React: {data}")
    global sensor_monitor
    
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
    
    # Salva preset se richiesto
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
    
    # Avvia ascolto sensore
    try:
        if sensor_monitor is None:
            sensor_monitor = SensorMonitor()
        
        sensor_monitor.set_config(
            corda=data.corda,
            assicuratore=data.assicuratore,
            operatore=data.operatore
        )
        sensor_monitor.start_monitoring()
        
        logger.info("🔊 BACKEND INIZIA ASCOLTO SENSORE")
        logger.info(f"   Corda: {data.corda}")
        logger.info(f"   Assicuratore: {data.assicuratore}")
        logger.info(f"   Operatore: {data.operatore}")
        
        response["monitoring_status"] = "STARTED"
        response["monitoring_info"] = "Backend in ascolto del sensore..."
        
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
    Ferma l'ascolto, analizza i dati e salva il record di caduta su file.
    """
    global sensor_monitor
    
    if sensor_monitor is None or not sensor_monitor.is_monitoring:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Backend non è in ascolto"
        )
    
    logger.info("⛔ OPERATORE: HO FATTO LA CADUTA")
    
    try:
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

# ==================== EXPORT CSV ====================

@router.get("/export/cadute.csv")
async def export_cadute_summary():
    """
    Scarica un CSV con TUTTE le cadute (una riga per caduta).
    Colonne: timestamp, corda, assicuratore, operatore, picco_N,
             offset_ms, durata_ms, letture_totali.
    Apribile direttamente in Excel italiano (delimiter ';').
    """
    csv_content = file_storage.export_cadute_summary_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cadute_summary.csv"}
    )

@router.get("/export/caduta/{index}.csv")
async def export_caduta_timeseries(index: int):
    """
    Scarica un CSV con la serie temporale di UNA caduta.
    Colonne: indice, timestamp_unix, offset_ms_da_inizio, value_N.
    index: 0 = prima caduta, -1 = ultima.
    """
    csv_content = file_storage.export_caduta_timeseries_csv(index)
    if csv_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caduta con indice {index} non trovata"
        )
    filename = f"caduta_{index}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ==================== DELETE ====================

@router.delete("/configurations/{config_id}")
async def delete_configuration(config_id: int, db: Session = Depends(get_db)):
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