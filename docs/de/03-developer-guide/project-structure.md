# Projektstruktur

```text
/
├── app.py                  # Einstieg
├── configuration.json      # Hauptkonfiguration
├── Dockerfile              # Containerdefinition
├── requirements.txt        # Python-Dependencies
├── docs/                   # Doku
├── init/                   # Init-Skripte (DB, Users)
├── models/                 # Mongo-Modelle
├── plugins/                # Plugin-System
│   ├── actions/            # Aktions-Implementierungen
│   ├── plugin_base.py      # Basis-Klasse
│   └── plugin_manager.py   # Plugin-Discovery
├── routes/                 # API/Web Routen
├── static/                 # Assets (CSS, JS, Images, Vendor)
├── templates/              # Jinja2 Templates
├── translations/           # i18n Dateien
├── utils/                  # Helper (DB, Auth, Execution...)
└── workdir/                # Laufzeit-Speicher für Kampagnen
```

## Wichtige Verzeichnisse

*   **`models/`**: Python-Klassen für MongoDB-Dokumente und CRUD.
*   **`routes/`**: Logik nach Modulen getrennt (Auth, API, Web UI).
*   **`plugins/actions/`**: Hier neue Fähigkeiten hinzufügen.
*   **`utils/`**: Kernlogik wie `campain_executor.py` (Runner).
