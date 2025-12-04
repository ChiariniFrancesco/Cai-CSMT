ISTRUZIONI PER ESEGUIRE IL CLIENT-SERVER IN AMBIENTE VIRTUALE:
NOTA: per riproducibilità si usa sui nostri computer un ambitente virtuale venv, sul rasberry non sarà necessario in quanto installeremo proprio nel suo ambiente tutti i requirements.txt

SETUP BACKEND
cd backend
python3 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt

SETUP FRONTEND --> siete ancora con venv attivo
cd frontend
npm install

AVVIARE IL SERVER
cd backend
source venv/bin/activate
python main.py

AVVIARE IL CLIENT
cd frontend
source venv/bin/activate
npm run dev

-------------------------

https://www.perplexity.ai/search/ora-mi-serve-il-tuo-aiuto-per-rrwhlCdnTB6PG.nzDikhdA#3 --> link alla chat usata per creare questo sistema