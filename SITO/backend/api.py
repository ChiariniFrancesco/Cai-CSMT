# backend/api.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import ConfigurationMemory
from schemas import ConfigurationCreate, ConfigurationResponse, SubmitFormData

router = APIRouter(prefix="/api", tags=["configurations"])

# ==================== GET ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Server is running"}

@router.get("/configurations", response_model=List[ConfigurationResponse])
async def get_all_configurations(db: Session = Depends(get_db)):
    """
    Ottieni TUTTE le configurazioni salvate
    Queste appariranno nel dropdown del client
    """
    configurations = db.query(ConfigurationMemory).all()
    return configurations

@router.get("/configurations/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(config_id: int, db: Session = Depends(get_db)):
    """Ottieni UNA configurazione specifica per ID"""
    config = db.query(ConfigurationMemory).filter(
        ConfigurationMemory.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configurazione con ID {config_id} non trovata"
        )
    
    return config

@router.get("/configurations/nome/{nome}", response_model=ConfigurationResponse)
async def get_configuration_by_name(nome: str, db: Session = Depends(get_db)):
    """Ottieni configurazione per NOME (usato dal dropdown)"""
    config = db.query(ConfigurationMemory).filter(
        ConfigurationMemory.nome_preset == nome
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configurazione '{nome}' non trovata"
        )
    
    return config

# ==================== POST ====================

@router.post("/submit", response_model=dict)
async def submit_form(data: SubmitFormData, db: Session = Depends(get_db)):
    """
    Ricevi i dati del form da React
    Se 'salva_come_preset' ha un valore, salva come configurazione memorizzata
    """
    print(f"📨 Dati ricevuti da React: {data}")
    
    response = {
        "status": "success",
        "message": "Dati ricevuti",
        "data": {
            "corda": data.corda,
            "assicuratore": data.assicuratore,
            "operatore": data.operatore
        }
    }
    
    # Se l'operatore vuole salvare come preset
    if data.salva_come_preset:
        try:
            # Controlla se esiste già
            existing = db.query(ConfigurationMemory).filter(
                ConfigurationMemory.nome_preset == data.salva_come_preset
            ).first()
            
            if existing:
                # Aggiorna se esiste
                existing.corda = data.corda
                existing.assicuratore = data.assicuratore
                existing.operatore = data.operatore
                db.commit()
                response["preset_saved"] = f"Preset '{data.salva_come_preset}' aggiornato"
            else:
                # Crea nuovo preset
                new_config = ConfigurationMemory(
                    nome_preset=data.salva_come_preset,
                    corda=data.corda,
                    assicuratore=data.assicuratore,
                    operatore=data.operatore
                )
                db.add(new_config)
                db.commit()
                response["preset_saved"] = f"Preset '{data.salva_como_preset}' creato"
        
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Errore nel salvare preset: {str(e)}"
            )
    
    return response

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
            detail=f"Configurazione con ID {config_id} non trovata"
        )
    
    db.delete(config)
    db.commit()
    
    return {"status": "success", "message": f"Configurazione {config_id} eliminata"}
