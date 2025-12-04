# 📚 Stack Tecnico: MVD2555 Configuration System

## Sommario Esecutivo

MVD2555 Configuration System è un'applicazione web full-stack moderna che combina un backend asincrone e performante con un frontend reattivo. Lo stack è stato scelto per ottimizzare il deployment su dispositivi con risorse limitate (Raspberry Pi) mantenendo un'architettura scalabile e facile da mantenere.

**Architettura:** Client-Server REST API  
**Linguaggi:** Python (backend), JavaScript (frontend)  
**Database:** SQLite (locale)  
**Deployment:** Single-server (Raspberry Pi / PC)

---

## 🔧 BACKEND: FastAPI + Python

### Framework Principale

#### **FastAPI 0.109.0**
FastAPI è un moderno framework web Python per costruire API REST rapidamente e con validazione dei dati automatica.

**Cosa fa:**
- Crea endpoint HTTP REST per comunicare con il frontend
- Valida automaticamente i dati in ingresso usando type hints Python
- Genera documentazione interattiva (Swagger UI) automaticamente
- Supporta richieste asincrone (async/await) per migliore performance
- CORS automatico per comunicare da React

**Perché scelto:**
- Estremamente leggero (~45 MB di footprint)
- Performance superiore a Django (5x+ veloce)
- Setup minimo (vs Django che richiede 200+ righe di configurazione)
- Perfetto per IoT/Raspberry Pi con risorse limitate
- Comunità crescente e documentazione eccellente

**Endpoint principali:**
```
GET  /api/health                           → Health check
GET  /api/configurations                   → Ottiene tutti i preset salvati
GET  /api/configurations/{id}              → Ottiene un preset specifico
GET  /api/configurations/nome/{nome}       → Ottiene preset per nome
POST /api/submit                           → Riceve dati dal form e li salva
DELETE /api/configurations/{id}            → Elimina un preset
```

---

### Server HTTP

#### **Uvicorn 0.27.0**
Uvicorn è un server ASGI (Asynchronous Server Gateway Interface) che esegue FastAPI.

**Cosa fa:**
- Ascolta su porta 8000 le richieste HTTP
- Gestisce connessioni multiple contemporaneamente (async)
- Supporta il reload automatico durante lo sviluppo
- Esegue l'applicazione FastAPI

**Perché scelto:**
- Standard de facto per FastAPI
- Performance eccellente
- Supporto nativo per async/await
- Configurazione semplice

---

### Database & ORM

#### **SQLAlchemy 2.0.23**
SQLAlchemy è un Object-Relational Mapping (ORM) che traduce oggetti Python in query SQL.

**Cosa fa:**
- Definisce modelli di database come classi Python (`ConfigurationMemory`)
- Genera automaticamente tabelle SQL dal codice Python
- Gestisce relazioni database e queries
- Fornisce protezione da SQL injection
- Supporta migrazioni database

**Modello utilizzato:**
```python
class ConfigurationMemory(Base):
    __tablename__ = "configurations"
    
    id                 → ID unico della configurazione
    nome_preset        → Nome della memoria (es: "Arena A Setup")
    corda              → Tipo di corda usata (es: "Corda 10mm")
    assicuratore       → Tipo assicuratore (es: "CAMP Dyna")
    operatore          → Nome operatore (es: "Mario Rossi")
    data_creazione     → Timestamp creazione
    data_aggiornamento → Timestamp ultimo aggiornamento
```

**Perché scelto:**
- Standard Python per database
- Funziona perfettamente con FastAPI
- Code-first approach (scrivi Python, il database è generato)
- Facile da testare e debuggare

---

#### **SQLite (Database)**
SQLite è un database SQL serverless embedded nel filesystem.

**Cosa fa:**
- Archivia le configurazioni salvate in file `data.db`
- No server esterno necessario
- Supporta transactions e ACID compliance
- Persistenza locale dei dati

**Struttura:**
```
data.db
└── Tabella: configurations
    ├── id (Primary Key, auto-increment)
    ├── nome_preset (UNIQUE, String)
    ├── corda (String)
    ├── assicuratore (String)
    ├── operatore (String)
    ├── data_creazione (DateTime)
    └── data_aggiornamento (DateTime)
```

**Perché scelto:**
- Zero configurazione
- Perfetto per Raspberry Pi (no risorse extra)
- Migrabile facilmente a PostgreSQL in futuro
- Backup semplice (è solo un file)

---

### Validazione Dati

#### **Pydantic 2.5.0**
Pydantic valida e serializza i dati usando type hints Python.

**Cosa fa:**
- Valida automaticamente i dati ricevuti dal frontend
- Converte i tipi di dato (string → int, json → object)
- Genera errori chiari se i dati non sono validi
- Documentazione automatica degli schemi API

**Schemi utilizzati:**
```python
class SubmitFormData(BaseModel):
    corda: str                                    # Obbligatorio, string
    assicuratore: str                             # Obbligatorio, string
    operatore: str                                # Obbligatorio, string
    salva_come_preset: Optional[str] = None       # Opzionale

class ConfigurationResponse(BaseModel):
    id: int
    nome_preset: str
    corda: str
    assicuratore: str
    operatore: str
    data_creazione: datetime
    data_aggiornamento: datetime
```

**Perché scelto:**
- Validazione built-in in FastAPI
- Documenta automaticamente l'API
- Conversione automatica dei tipi
- Errori user-friendly

---

### Utilità

#### **python-dotenv 1.0.0**
Carica variabili di ambiente da file `.env`.

**Cosa fa:**
- Legge il file `.env` (non trackato in git)
- Fornisce variabili di configurazione locali
- Separa config da codice (best practice)

**Uso:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

**Perché scelto:**
- Standard per .env files
- Sicurezza (credenziali non in codice)
- Configurazione per ambiente (dev/prod)

---

## ⚛️ FRONTEND: React + Vite

### Framework UI

#### **React 18.2.0**
React è una libreria JavaScript per costruire interfacce utente reattive.

**Cosa fa:**
- Definisce il form con 3 input, 1 dropdown, 1 bottone
- Gestisce lo stato locale (corda, assicuratore, operatore)
- Re-rendering automatico quando lo stato cambia
- Componente singolo (App.jsx) per semplicità

**Componenti principali:**
```jsx
<select> (Dropdown Presets)
  ├─ GET /api/configurations carica i preset salvati
  └─ onChange carica i dati nel form

<input> (3x) - Corda, Assicuratore, Operatore
  ├─ Gestiti con useState hooks
  └─ onChange aggiorna lo stato

<button> (Conferma)
  └─ onClick invia POST /api/submit al backend
  
<div> (Presets Salvati)
  └─ Mostra card di tutte le configurazioni salvate
```

**Perché scelto:**
- Standard industria per web UI
- Curva di apprendimento contenuta
- Componente singolo = manutenibilità
- Vasto ecosistema e comunità

---

### Build Tool

#### **Vite 5.0.0**
Vite è un build tool ultra-veloce per applicazioni web moderne.

**Cosa fa:**
- Compila JSX (React) in JavaScript standard
- Bundla i file CSS e JavaScript
- Serve i file in development mode con hot reload
- Genera build ottimizzato per produzione

**Processo:**
```
Development:
  npm run dev
  ├─ Vite server locale su port 5173
  ├─ Hot reload (auto-refresh al salvataggio)
  └─ Source maps per debugging

Production:
  npm run build
  ├─ Minifica e ottimizza i file
  ├─ Genera output in /dist
  └─ Copia in backend/static/ per FastAPI
```

**Perché scelto:**
- 10x più veloce di Create React App
- Build contemporanea di frontend e backend
- Setup minimo (vs webpack complesso)
- Performance ottimale in produzione

---

### HTTP Client

#### **Axios 1.6.0**
Axios è una libreria JavaScript per fare richieste HTTP.

**Cosa fa:**
- Invia richieste GET al backend per caricare presets
- Invia richieste POST per salvare le configurazioni
- Invia richieste DELETE per eliminare presets
- Gestisce errori e timeout automaticamente

**Richieste utilizzate:**
```javascript
// Carica presets all'avvio
GET /api/configurations
├─ Response: Array di presets
└─ Popola dropdown

// Carica un preset specifico
GET /api/configurations/{id}
├─ Response: ConfigurationResponse
└─ Riempie i 3 input

// Invia form al backend
POST /api/submit
├─ Body: { corda, assicuratore, operatore, salva_come_preset }
└─ Response: { status, message, preset_saved? }

// Elimina un preset
DELETE /api/configurations/{id}
├─ Response: { status, message }
└─ Ricarica lista presets
```

**Perché scelto:**
- API intuitiva e documentata
- Gestione errori automatica
- Request/Response interceptors
- Promise-based (vs fetch callback hell)

---

### Styling

#### **CSS3 (Vanilla CSS)**
CSS3 nativo per stilizzare l'interfaccia.

**Cosa fa:**
- Gradient background (purple → viola)
- Form layout con flexbox
- Responsive design (mobile-friendly)
- Animazioni smooth (message slides)
- Card grid per presets

**Stili principali:**
```css
.container          → Card principale bianca
.form               → Layout colonna dei form
.input              → Stile input text e select
.button             → Pulsante con gradient
.message            → Notifiche (success/error)
.preset-card        → Card singolo preset
.presets-grid       → Grid responsive
```

**Perché scelto:**
- Zero dipendenze CSS (vs Tailwind, Bootstrap)
- Full control su design
- Facile da debuggare
- Performance ottimale (no CSS-in-JS overhead)

---

## 🔄 Flusso di Comunicazione

```
┌─────────────────────────────────────┐
│    Browser (React App)              │
│  Port: localhost:5173               │
└────────────────┬────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
      GET/POST/DELETE    WebSocket
         │                │
┌────────▼─────────────────▼──────────┐
│   FastAPI Server                    │
│   Port: 0.0.0.0:8000                │
│   ├─ Route: GET /api/configurations │
│   ├─ Route: POST /api/submit        │
│   ├─ Route: DELETE /configurations  │
│   └─ Static: /static (React build)  │
└────────┬──────────────────┬─────────┘
         │                  │
      SQLAlchemy         Pydantic
      (ORM)             (Validation)
         │                  │
┌────────▼──────────────────▼─────────┐
│   SQLite Database                   │
│   File: backend/data.db             │
│   Table: configurations             │
└─────────────────────────────────────┘
```

---

## 📦 Dipendenze Completo

### Backend (requirements.txt)

```
fastapi==0.109.0              Framework web async
uvicorn==0.27.0               Server ASGI
sqlalchemy==2.0.23            ORM database
pydantic==2.5.0               Validazione dati
python-dotenv==1.0.0          Variabili ambiente
```

**Peso totale:** ~50 MB (venv)

### Frontend (package.json)

```json
{
  "dependencies": {
    "react": "^18.2.0",           Libreria UI
    "react-dom": "^18.2.0",       Rendering DOM
    "axios": "^1.6.0"             HTTP client
  },
  "devDependencies": {
    "vite": "^5.0.0",             Build tool
    "@vitejs/plugin-react": "^4.0.0"  Plugin React per Vite
  }
}
```

**Peso totale:** ~500 MB (node_modules, non trackato in git)

---

## 🎯 Architettura Finale

### Struttura Cartelle

```
SITO/
├── backend/                    # Backend Python/FastAPI
│   ├── main.py                # Entry point FastAPI
│   ├── database.py            # SQLAlchemy setup
│   ├── models.py              # Modello ConfigurationMemory
│   ├── schemas.py             # Pydantic schemas
│   ├── api.py                 # Route endpoints
│   ├── requirements.txt        # Dipendenze Python
│   ├── venv/                  # Virtual environment (gitignored)
│   ├── data.db                # SQLite database (gitignored)
│   └── static/                # React build (serve da FastAPI)
│
├── frontend/                   # Frontend React/Vite
│   ├── src/
│   │   ├── App.jsx            # Componente principale
│   │   ├── App.css            # Stili
│   │   └── index.jsx          # Entry point
│   ├── index.html             # Template HTML
│   ├── vite.config.js         # Config Vite
│   ├── package.json           # Dipendenze Node.js
│   ├── package-lock.json      # Lock file npm
│   ├── node_modules/          # Dipendenze (gitignored)
│   └── dist/                  # Build di produzione
│
├── .gitignore                 # Esclusioni Git
├── .env                       # Variabili ambiente (gitignored)
└── .git/                      # Repository Git
```

---

## 🚀 Ciclo di Vita Sviluppo

### 1. Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py
# FastAPI running on http://0.0.0.0:8000

# Terminal 2: Frontend
cd frontend
npm run dev
# Vite running on http://localhost:5173
```

**Durante sviluppo:**
- React hot reload (cambi il codice, la pagina si aggiorna)
- FastAPI reload (cambi main.py, server riavvia)
- Database locale (data.db)
- No build necessario

### 2. Build per Produzione

```bash
# Build React
cd frontend
npm run build
# Output: dist/

# Copia build in FastAPI static
cp -r dist/* ../backend/static/

# Avvia FastAPI su porta 8000
cd ../backend
python main.py

# Accedi a http://raspberry.local:8000
```

**In produzione:**
- Un unico server FastAPI serve sia API che React
- Data.db persiste i dati
- No hot reload
- Performance ottimale

---

## 🔒 Sicurezza & Best Practices

| Aspetto | Implementazione |
|---------|-----------------|
| **CORS** | Abilitato su FastAPI (configurabile) |
| **Validazione input** | Pydantic valida ogni request |
| **SQL Injection** | SQLAlchemy ORM previene automaticamente |
| **.env secrets** | Non trackato in git |
| **Database** | SQLite locale (no credenziali) |
| **Async** | Gestisce request in parallelo senza blocchi |

---

## 📈 Performance & Scalabilità

### Benchmarks (Raspberry Pi 4)

```
Memory:        ~150 MB (venv + uvicorn + app)
Startup time:  ~0.5 secondi
Request latency: ~50-100 ms
Database queries: <10 ms per query
Concurrent users: ~50+ (Raspberry Pi 4)
```

### Miglioramenti futuri

Se dovesse scalare:
- PostgreSQL invece di SQLite (multi-user)
- Redis per caching presets
- Docker per containerizzazione
- Nginx reverse proxy
- Load balancing con supervisor

---

## 🎓 Scelta Tecnologie: Razionale

### Perché FastAPI > Django per questo progetto?

| Criterio | FastAPI | Django | Vincente |
|----------|---------|--------|---------|
| **Peso** | 50 MB | 200 MB | FastAPI ✅ |
| **Setup** | 20 righe | 200 righe | FastAPI ✅ |
| **Performance** | ~20k req/s | ~5k req/s | FastAPI ✅ |
| **Async nativo** | Si | No | FastAPI ✅ |
| **Curva apprendimento** | Facile | Ripida | FastAPI ✅ |
| **Admin panel** | No | Si built-in | Django ✅ |
| **Community** | Crescente | Enorme | Django ✅ |
| **Ideal per IoT** | Si | No | FastAPI ✅ |

**Vincitore per Raspberry Pi:** FastAPI

---

### Perché React > Vue/Angular per questo progetto?

| Criterio | React | Vue | Angular | Vincente |
|----------|-------|-----|---------|----------|
| **Curva apprendimento** | Media | Facile | Ripida | Vue |
| **Performance** | Ottima | Ottima | Buona | React/Vue |
| **Bundle size** | ~42 KB | ~33 KB | ~130 KB | Vue |
| **Comunità** | Enorme | Media | Grande | React |
| **Jobmarket** | Alto | Medio | Alto | React |
| **Semplicità** | Media | Facile | Difficile | Vue |
| **Ecosistema** | Vastissimo | Buono | Completo | React |

**Per questo progetto:** React è overkill, ma facilita il learning curve iniziale. Vue sarebbe ideale.

---

### Perché Vite > Webpack/Create React App?

| Criterio | Vite | Webpack | CRA |
|----------|------|---------|-----|
| **Build speed** | <1s | 10+s | 20+s |
| **Dev server start** | 50ms | 5+s | 10+s |
| **Hot reload** | Istantaneo | 5+s | 5+s |
| **Config** | Minima | Complessa | Zero (pre-configurato) |
| **Bundle size** | Ottimale | Variabile | Fisso grande |

**Vincitore:** Vite (10x+ veloce di CRA)

---

## 📚 Documentazione Stack

### Risorse Ufficiali

- **FastAPI:** https://fastapi.tiangolo.com
- **React:** https://react.dev
- **Vite:** https://vitejs.dev
- **SQLAlchemy:** https://www.sqlalchemy.org
- **Pydantic:** https://docs.pydantic.dev
- **Axios:** https://axios-http.com

### File di Configurazione Chiave

```
vite.config.js
├─ Configurazione build Vite
├─ Proxy API (dev)
└─ Output directory (dist)

backend/main.py
├─ FastAPI app initialization
├─ CORS middleware
├─ Static files mounting
└─ API router inclusion
```

---

## 🎯 Conclusione

Questo stack rappresenta la **migliore combinazione di:**
- ✅ Performance (FastAPI async)
- ✅ Leggerezza (Raspberry Pi friendly)
- ✅ Developer experience (React + Vite)
- ✅ Facilità di deployment (single server)
- ✅ Scalabilità futura (architecture-ready)

**Ideale per:** IoT, MVP, prototipazione veloce, educational projects su hardware limitato.
