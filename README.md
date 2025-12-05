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

V1 --> versione funzionante del sistema client-server che usa fastAPI come backend e React come frontend con alcune librerie a supporto di entrambi per gestire bene il tutto

V2 --> la v2 è una copia della v1 + integrazione per leggere i dati dal sensore (per test creati sintetici poi possiamo attaccare arduino per simulare) e che manda i dati del sensore + quelli della configurazione decisi dal client a firestore (solo quando ENTRAMBI sono disponibili) --> devo ancora testarlo

V2.1 ---> versione come V2 ma che non integra firestore ma semplicemente un fule txt, per permetterci di fare testing senza avere ancora il database cloud

to do per v2:
Vai in Firebase Console
https://console.firebase.google.com
Progetto → Settings → Service Accounts
Generate new private key
Scarica il JSON
Salva come backend/serviceAccountKey.json
Aggiungi a .gitignore

echo "serviceAccountKey.json" >> .gitignore -----> riguardo a questo credo che .env vada tolto dal gitignore in quanto ci serve sapere le configurazioni e i dati non sono sensibili tra di noi

- creare account googl per firestore
- provare a fare una versione che non abbia bisogno di direstore => V2.1 done
 

