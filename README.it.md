# TestGyver

## Scegli la lingua
- [Français](README.md)
- [English](README.en.md)
- [Español](README.es.md)
- [Deutsch](README.de.md)
- Italiano (questo documento)

## Panoramica
TestGyver è una piattaforma di testing web multi-ambiente pensata per orchestrare, eseguire e documentare campagne complesse. Ispirata all'inventiva di MacGyver, combina un sistema di azioni estensibile con reportistica dettagliata e strumenti di amministrazione.

## Funzionalità principali
- Flusso di autenticazione con JWT e pagina di login dedicata (`/`).
- Dashboard post-login (`/dashboard`) con elenco campagne e scorciatoie per gli amministratori.
- Gestione completa di campagne, test e report di esecuzione.
- Moduli amministrativi per gestire utenti e variabili per ambiente.
- Catalogo di azioni estensibile (HTTPRequest, WebDAV, FTP, SFTP, SSH, ecc.) basato su maschere JSON.
- Documentazione interattiva dell'API disponibile su `/swagger`.

## Stack tecnologico
- **Backend / Frontend:** Flask, Jinja2, Bootstrap, FontAwesome.
- **Database:** MongoDB (`users`, `variables`, `campains`, `tests`, `rapports`).
- **Persistenza:** PyMongo.
- **Sicurezza:** JWT con scadenza configurabile e controllo dei ruoli.
- **Configurazione:** `configuration.json` centralizza MongoDB, applicazione, paginazione, sicurezza e versione.
- **Asset statici:** in `static/` con CDN locali.

## Requisiti
- Python 3.11 o superiore
- MongoDB 6.x (o compatibile)
- `pip` e un gestore di ambienti virtuali (`venv`, `virtualenv`, ...)
- Opzionale: Node.js per estendere gli asset frontend

## Installazione
1. Clona il repository:
   ```bash
   git clone <url-repo> && cd app_test
   ```
2. Crea e attiva un ambiente virtuale:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

## Configurazione
1. Crea `configuration.json` (o copia un modello):
   ```json
   {
       "mongo": {
           "user": "root",
           "pass": "mypass",
           "host": "localhost",
           "port": "27017",
           "bdd": "testGyver"
       },
       "jwt_secret": "change-me",
       "app": {
           "debug": true,
           "port": 5000
       },
       "pagination": {
           "page_size": 20
       },
       "security": {
           "token_expiration_minutes": 60
       },
       "version": "1.0.0"
   }
   ```
2. Aggiungi un file `.env` (ignorato da Git) per le variabili sensibili se necessario.

## Esecuzione locale
1. Avvia MongoDB e verifica le credenziali.
2. Esporta le variabili di ambiente di Flask:
   ```bash
   export FLASK_APP=app
   export FLASK_ENV=development
   ```
3. Avvia l'applicazione:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```
4. Apri `http://localhost:5000` nel browser.

## Script utili
- `start.sh`: script di avvio standard (usato anche nel container Docker). Rendi il file eseguibile con `chmod +x start.sh`.
- CLI `flask`: per manutenzione, creazione utenti admin, seed di dati, ecc.

## Flusso Docker
1. Costruisci l'immagine:
   ```bash
   docker build -t testgyver:latest .
   ```
2. Avvia il container:
   ```bash
   docker run -p 5000:5000 --env-file .env testgyver:latest
   ```
3. Monta il tuo `configuration.json` se vuoi mantenerlo all'esterno:
   ```bash
   docker run -p 5000:5000 \
       -v $(pwd)/configuration.json:/app/configuration.json \
       --env-file .env \
       testgyver:latest
   ```

## Debug in VS Code
1. Installa l'estensione Python e seleziona l'interprete corretto.
2. Apri il progetto in VS Code.
3. Seleziona **TestGyver: Flask Debug** e avvia il debugger.
4. Imposta i breakpoint necessari e avvia la sessione.

## Modello dati
- `users`: informazioni utente, password hashata e ruolo.
- `variables`: coppie chiave/valore raggruppate per ambiente (`filiere`).
- `campains`: metadati della campagna (autore, descrizione, data).
- `tests`: elenco di azioni associato a una campagna.
- `rapports`: risultati di esecuzione, stato per test e log.

## API principali
- `POST /api/login`, `POST /api/logout` per il ciclo JWT.
- Endpoint CRUD per `/api/users`, `/api/campains`, `/api/tests`, `/api/variables`, `/api/rapports`.
- Documentazione interattiva su `/swagger`.

## Estendere le azioni
Ogni classe in `plugins/actions` estende `ActionBase` e deve:
- fornire una maschera JSON con i campi configurabili;
- implementare `execute(ActionContext)` con la logica specifica;
- restituire le tracce da utilizzare nei report.

## Prossimi passi
- Crea nuove azioni derivando da `ActionBase`.
- Integra TestGyver nelle pipeline CI/CD per pianificare le campagne.
- Aggiungi canali di notifica (Slack, email, Teams) per diffondere i report.

## Supporto
Apri una issue su GitHub o contatta il team TestGyver per domande e richieste.
