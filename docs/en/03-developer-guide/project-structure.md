# Project Structure

```text
/
├── app.py                  # Application entry point
├── configuration.json      # Main configuration file
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── docs/                   # Documentation (You are here)
├── init/                   # Initialization scripts (DB, Users)
├── models/                 # Database models (User, Campain, Test...)
├── plugins/                # Plugin system
│   ├── actions/            # Action plugins implementation
│   ├── plugin_base.py      # Base class for all plugins
│   └── plugin_manager.py   # Plugin discovery logic
├── routes/                 # API and Web routes (Blueprints)
├── static/                 # Static assets (CSS, JS, Images, Vendor libs)
├── templates/              # Jinja2 HTML templates
├── translations/           # i18n translation files
├── utils/                  # Helper modules (DB, Auth, Execution...)
└── workdir/                # Runtime storage for campaigns
```

## Key Directories

*   **`models/`**: Contains Python classes representing MongoDB documents. They handle CRUD operations.
*   **`routes/`**: Separates the application logic into modules (Auth, API, Web UI).
*   **`plugins/actions/`**: This is where you add new capabilities to the system.
*   **`utils/`**: Contains the core logic for complex tasks like `campain_executor.py` (the test runner).
