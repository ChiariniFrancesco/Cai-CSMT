# ISTRUZIONI PER ESEGUIRE IL CLIENT-SERVER IN AMBIENTE VIRTUALE

> **NOTA:** per riproducibilità si usa sui nostri computer un ambiente virtuale `venv`, sul Raspberry non sarà necessario in quanto installeremo direttamente nel suo ambiente tutti i `requirements.txt`.

---

## SETUP BACKEND

```
cd backend
python3 -m venv venv 
source venv/bin/activate
pip install -r requirements.txt
```

---

## SETUP FRONTEND  
*(siete ancora con venv attivo)*

```
cd frontend
npm install
```

---

## AVVIARE IL SERVER

```
cd backend
source venv/bin/activate
python main.py
```

---

## AVVIARE IL CLIENT

```
cd frontend
source venv/bin/activate
npm run dev
```

---

## LINK RIFERIMENTO

[https://www.perplexity.ai/search/ora-mi-serve-il-tuo-aiuto-per-rrwhlCdnTB6PG.nzDikhdA#3](https://www.perplexity.ai/search/ora-mi-serve-il-tuo-aiuto-per-rrwhlCdnTB6PG.nzDikhdA#3)  
→ Link alla chat usata per creare questo sistema

---

## VERSIONI

### **V1**
Versione funzionante del sistema client-server che usa **FastAPI** come backend e **React** come frontend, con alcune librerie a supporto di entrambi per gestire bene il tutto.

---

### **V2**
Copia della **V1** + integrazione per:
- Leggere i dati dal sensore (per test creati sinteticamente; poi si potrà connettere Arduino per simulare).  
- Mandare i dati del sensore + quelli della configurazione decisi dal client a **Firestore** (solo quando *entrambi* sono disponibili).

💡 *Da testare.*

---

### **V2.1**
Versione come **V2** ma che non integra **Firestore**, bensì un semplice file `.txt`, per permettere il **testing senza database cloud**.

---

## TO DO PER V2

1. Vai in **Firebase Console**  
   → [https://console.firebase.google.com](https://console.firebase.google.com)
2. Progetto → Settings → **Service Accounts**
3. **Generate new private key**
4. Scarica il **JSON**
5. Salva come:  
   `backend/serviceAccountKey.json`
6. Aggiungi a `.gitignore`

```
echo "serviceAccountKey.json" >> .gitignore
```

> Riguardo a questo: credo che `.env` vada **tolto** dal `.gitignore` in quanto ci serve sapere le configurazioni e i dati non sono sensibili tra di noi.

---

### Da fare

- Creare account Google per **Firestore**  
- Provare a fare una versione che non abbia bisogno di Firestore → ✅ **V2.1 done**
- fare una v2.2 dove abbiamo nel client un tast conferma 1 e conferma 2 per sapere quando iniza e quando finisce la rilevazione del piccho
- fare v 2.3 dove a differenza della 2.2 nmanteniamo un tasto e il sistema tiene traccia di tutti i piacchi e della time sereis del segnale e l'operatore supponiamo che faccia i test. su un'unica configurazione, allora la mette solo una volta e a posteriori si analizzeranno i vari picchi si troveranno x picchi corrispondenti a x rielvazion ie si associeranno i loro timestamps alla configurazione e creeraznno le rilevazioni
```

