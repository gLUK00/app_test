# Manuelle Installation

Folge diesen Schritten, um TestGyver direkt auf deinem Rechner zu installieren und zu starten.

## 1. Repository klonen

```bash
git clone <repository-url>
cd app_test
```

## 2. Virtuelle Umgebung einrichten

Wir empfehlen eine virtuelle Umgebung für Abhängigkeiten.

```bash
# Virtuelle Umgebung erstellen
python3 -m venv .venv

# Aktivieren
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

## 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

## 4. Konfiguration

1.  Kopiere die Beispielkonfiguration (falls vorhanden) oder lege `configuration.json` im Root an.
2.  Siehe [Konfigurations-Guide](configuration.md) für Details.

## 5. Datenbank initialisieren (Optional)

Du kannst die DB mit Startdaten/Indizes befüllen.

```bash
python init/init_database.py
```

Admin-User anlegen:
```bash
python init/create_user.py
```

## 6. Anwendung starten

```bash
# Umgebungsvariablen
export FLASK_APP=app
export FLASK_ENV=development  # Für Deployment 'production'

# Flask starten
flask run --host=0.0.0.0 --port=8080
```

Zugriff unter `http://localhost:8080`.
