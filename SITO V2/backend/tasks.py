# backend/tasks.py
"""
Task scheduler - esegue processi in background
- Raccoglie dati da MVD2555 ogni 5 secondi
- Raccoglie dati da fonte esterna ogni 5 secondi
- Quando ENTRAMBI presenti, li combina e invia a Firebase
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from external_data_collector import DataAggregator
from firebase_manager import FirebaseManager

logger = logging.getLogger(__name__)

# Istanze globali
aggregator = DataAggregator()
firebase = FirebaseManager()
scheduler = None

async def collect_and_send_task():
    """
    Task principale che:
    1. Raccoglie dati da MVD2555
    2. Raccoglie dati da fonte esterna
    3. Li combina quando ENTRAMBI disponibili
    4. Li invia a Firebase
    """
    logger.info("🔄 Inizio raccolta dati...")
    
    try:
        # Raccoglie dati combinati da entrambe le sorgenti
        combined_data = await aggregator.get_combined_data()
        
        if combined_data is None:
            logger.warning("⚠️ Dati combinati non disponibili")
            return
        
        # Invia a Firebase
        success = firebase.send_data(
            data=combined_data,
            path='measurements'
        )
        
        if success:
            logger.info(f"✅ Dati inviati a Firebase: {combined_data}")
        else:
            logger.error("❌ Errore invio Firebase")
            
    except Exception as e:
        logger.error(f"❌ Errore task: {e}")

def start_scheduler():
    """Avvia il scheduler di background tasks"""
    global scheduler
    
    try:
        scheduler = AsyncIOScheduler()
        
        # Aggiungi il task che raccoglie e invia dati ogni 5 secondi
        scheduler.add_job(
            collect_and_send_task,
            trigger=IntervalTrigger(seconds=5),
            id='collect_and_send',
            name='Collect data from sources and send to Firebase',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("✅ Task scheduler avviato")
        
    except Exception as e:
        logger.error(f"❌ Errore avvio scheduler: {e}")

def stop_scheduler():
    """Ferma il scheduler"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        logger.info("❌ Task scheduler fermato")
