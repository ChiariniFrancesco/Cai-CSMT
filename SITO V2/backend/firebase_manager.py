# backend/firebase_manager.py
"""
Gestione Firebase Realtime Database
Invia i dati combinati a Firebase
"""

import firebase_admin
from firebase_admin import credentials, db
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Manager per Firebase Realtime Database"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - una sola istanza"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inizializza Firebase una sola volta"""
        if not FirebaseManager._initialized:
            self._initialize_firebase()
            FirebaseManager._initialized = True
    
    def _initialize_firebase(self):
        """Inizializza Firebase Admin SDK"""
        try:
            # Leggi credenziali dal file .env
            service_account_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            firebase_db_url = os.getenv('FIREBASE_DB_URL')
            
            if not service_account_path or not firebase_db_url:
                logger.warning("⚠️ Firebase credentials non configurate in .env")
                self.is_ready = False
                return
            
            # Inizializza Firebase Admin SDK
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': firebase_db_url
            })
            
            self.is_ready = True
            logger.info("✅ Firebase inizializzato")
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione Firebase: {e}")
            self.is_ready = False
    
    def send_data(self, data: Dict[str, Any], path: str = 'measurements') -> bool:
        """
        Invia dati a Firebase Realtime Database
        
        Args:
            data: Dizionario dei dati da inviare
            path: Percorso in Firebase (default: 'measurements')
        
        Returns:
            True se successo, False se errore
        """
        if not self.is_ready:
            logger.error("❌ Firebase non è pronto")
            return False
        
        try:
            ref = db.reference(path)
            ref.push(data)  # Push aggiunge un nuovo record con timestamp auto
            logger.info(f"✅ Dati inviati a Firebase: {path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore invio Firebase: {e}")
            return False
    
    def get_data(self, path: str = 'measurements') -> Optional[Dict]:
        """
        Legge dati da Firebase Realtime Database
        """
        if not self.is_ready:
            return None
        
        try:
            ref = db.reference(path)
            return ref.get()
        except Exception as e:
            logger.error(f"❌ Errore lettura Firebase: {e}")
            return None
