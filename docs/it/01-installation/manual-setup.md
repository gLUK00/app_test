# Installazione Manuale

Segui questi passi per installare ed eseguire TestGyver localmente.

## 1. Clona il Repository

```bash
git clone <repository-url>
cd app_test
```

## 2. Crea l'Ambiente Virtuale

Raccomandato per gestire le dipendenze.

```bash
python3 -m venv .venv

# Attiva
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
```

## 3. Installa le Dipendenze

```bash
pip install -r requirements.txt
```

## 4. Configurazione

1.  Copia la configurazione di esempio (se presente) o crea `configuration.json` nella root.
2.  Vedi la [Guida Configurazione](configuration.md).

## 5. Inizializza il Database (Opzionale)

Puoi pre-popolare la base dati e gli indici.

```bash
python init/init_database.py
```

Per creare un admin:
```bash
python init/create_user.py
```

## 6. Avvia l'Applicazione

```bash
export FLASK_APP=app
export FLASK_ENV=development  # Usa 'production' in deploy

flask run --host=0.0.0.0 --port=5000
```

Apri `http://localhost:5000`.
