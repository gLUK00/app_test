# TestGyver

## Sprache wählen
- [Français](README.md)
- [English](README.en.md)
- [Español](README.es.md)
- Deutsch (dieses Dokument)
- [Italiano](README.it.md)

## Überblick
TestGyver ist eine Multi-Umgebungs-Testplattform für Webanwendungen. Sie dient dazu, Testkampagnen zu planen, durchzuführen und nachvollziehbar zu dokumentieren. Angelehnt an die Kreativität von MacGyver kombiniert die Lösung ein flexibles Aktions-Plugin-System mit aussagekräftigen Reports und Administrationsfunktionen.

## Zentrale Funktionen
- JWT-geschützter Login-Prozess mit eigener Anmeldeseite (`/`).
- Dashboard nach dem Login (`/dashboard`) mit Kampagnenliste und Admin-Schnellaktionen.
- Vollständige Verwaltung von Kampagnen, Tests und Ausführungsberichten.
- Administrationsmodule zur Pflege von Benutzern und umgebungsspezifischen Variablen.
- Erweiterbarer Aktionskatalog (HTTPRequest, WebDAV, FTP, SFTP, SSH usw.) auf Basis von JSON-Eingabemasken.
- Interaktive API-Dokumentation über `/swagger`.

## Technologiestack
- **Backend / Frontend:** Flask, Jinja2, Bootstrap, FontAwesome.
- **Datenbank:** MongoDB (`users`, `variables`, `campains`, `tests`, `rapports`).
- **Persistenz:** PyMongo.
- **Sicherheit:** JWT mit konfigurierbarer Ablaufzeit und rollenbasierter Zugriffskontrolle.
- **Konfiguration:** `configuration.json` bündelt MongoDB-, App-, Paginierungs-, Sicherheits- und Versionsparameter.
- **Statische Assets:** liegen in `static/` und werden lokal ausgeliefert.

## Voraussetzungen
- Python 3.11 oder höher
- MongoDB 6.x (oder kompatibel)
- `pip` sowie ein virtuelles Umfeld (`venv`)
- Optional: Node.js zur Erweiterung der Frontend-Ressourcen

## Installation
1. Repository klonen:
   ```bash
   git clone <repo-url> && cd app_test
   ```
2. Virtuelle Umgebung anlegen und aktivieren:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

## Konfiguration
1. `configuration.json` erstellen (oder Vorlage kopieren):
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
2. Optional: `.env` für sensible Variablen anlegen (wird von Git ignoriert).

## Lokaler Betrieb
1. MongoDB starten und Zugangsdaten prüfen.
2. Flask-Variablen exportieren:
   ```bash
   export FLASK_APP=app
   export FLASK_ENV=development
   ```
3. Anwendung starten:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```
4. Browser öffnen und `http://localhost:5000` aufrufen.

## Nützliche Skripte
- `start.sh`: Standard-Startskript (auch für Docker). Mit `chmod +x start.sh` ausführbar machen.
- `flask` CLI: Wartungsaufgaben, Anlegen von Admins, Seed-Daten usw.

## Docker-Workflow
1. Image bauen:
   ```bash
   docker build -t testgyver:latest .
   ```
2. Container starten:
   ```bash
   docker run -p 5000:5000 --env-file .env testgyver:latest
   ```
3. Optional `configuration.json` einbinden:
   ```bash
   docker run -p 5000:5000 \
       -v $(pwd)/configuration.json:/app/configuration.json \
       --env-file .env \
       testgyver:latest
   ```

## Debugging mit VS Code
1. Python-Erweiterung installieren und Interpreter wählen.
2. Projekt in VS Code öffnen.
3. Konfiguration **TestGyver: Flask Debug** starten.
4. Breakpoints setzen und den Debugger ausführen.

## Datenmodell
- `users`: Nutzerinformationen, Passwort-Hash, Rolle.
- `variables`: Schlüssel/Wert-Paare, gruppiert nach Umgebung (`filiere`).
- `campains`: Kampagnen-Metadaten (Ersteller, Beschreibung, Datum).
- `tests`: Aktionen einer Kampagne.
- `rapports`: Ausführungsresultate inkl. Logs pro Test.

## Wichtige APIs
- `POST /api/login`, `POST /api/logout` für den JWT-Zyklus.
- CRUD-Endpunkte für `/api/users`, `/api/campains`, `/api/tests`, `/api/variables`, `/api/rapports`.
- Interaktive Dokumentation über `/swagger`.

## Aktionen erweitern
Jede Klasse in `plugins/actions` erweitert `ActionBase` und muss:
- eine JSON-Eingabemaske liefern;
- `execute(ActionContext)` implementieren;
- Ausführungs-Logs für die Reports zurückgeben.

## Nächste Schritte
- Eigene Aktionen entwickeln, indem `ActionBase` erweitert wird.
- TestGyver in CI/CD-Pipelines integrieren (GitHub Actions, Jenkins, GitLab).
- Benachrichtigungen (Slack, E-Mail, Teams) für Testergebnisse einbinden.

## Support
Bitte eröffnen Sie ein GitHub-Issue oder kontaktieren Sie das TestGyver-Team bei Fragen und Anregungen.
