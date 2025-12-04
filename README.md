ISTRUZIONI PER ESEGUIRE IL SITO IN AMBIENTE VIRTUALE:

# SETUP BACKEND

# 1. Entra nella cartella backend
cd backend

# 2. Crea virtual environment (Python) --> io uso python3 ma sui vostri pc potreste avere python
python3 -m venv venv 

# 3. Attiva virtual environment
source venv/bin/activate

# 4. Installa le dipendenze Python
pip install -r requirements.txt

# SETUP BACKEND --> siete ancora con venv attivo

 1. Torna nella cartella SITO (root)
cd ..

# 2. Entra in frontend
cd frontend

# 3. Installa dipendenze Node.js
npm install

# AVVIARE IL SERVER

# vai in backend
cd backend

# Attiva venv se non attivo
source venv/bin/activate

# Avvia FastAPI
python main.py

# ---------------------------------------------------------------------------------------------------------------------------------------

Qua metterò una spiegazione della struttura dell'architettura client - server ...