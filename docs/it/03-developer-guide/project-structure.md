# Struttura del Progetto

```text
/
├── app.py                  # Entry point
├── configuration.json      # Configurazione
├── Dockerfile              # Container
├── requirements.txt        # Dipendenze
├── docs/                   # Documentazione
├── init/                   # Script init (DB, Users)
├── models/                 # Modelli Mongo
├── plugins/                # Sistema plugin
│   ├── actions/            # Implementazioni
│   ├── plugin_base.py      # Base class
│   └── plugin_manager.py   # Discovery
├── routes/                 # Rotte API/Web
├── static/                 # Asset (CSS, JS, immagini, vendor)
├── templates/              # Template Jinja2
├── translations/           # File i18n
├── utils/                  # Helper (DB, Auth, Execution...)
└── workdir/                # Storage runtime per campagne
```

## Directory Chiave

*   **`models/`**: Classi Python per documenti MongoDB e CRUD.
*   **`routes/`**: Logica separata per modulo (Auth, API, Web UI).
*   **`plugins/actions/`**: Dove aggiungere nuove capacità.
*   **`utils/`**: Logica core come `campain_executor.py` (runner).
