# Estructura del Proyecto

```text
/
├── app.py                  # Punto de entrada
├── configuration.json      # Configuración principal
├── Dockerfile              # Definición de contenedor
├── requirements.txt        # Dependencias Python
├── docs/                   # Documentación
├── init/                   # Scripts de inicialización (DB, Users)
├── models/                 # Modelos MongoDB (User, Campain, Test...)
├── plugins/                # Sistema de plugins
│   ├── actions/            # Implementación de plugins de acción
│   ├── plugin_base.py      # Clase base
│   └── plugin_manager.py   # Descubrimiento de plugins
├── routes/                 # Rutas API y Web (Blueprints)
├── static/                 # Assets estáticos (CSS, JS, imágenes, vendor)
├── templates/              # Plantillas Jinja2
├── translations/           # Archivos de traducción i18n
├── utils/                  # Helpers (DB, Auth, Execution...)
└── workdir/                # Almacenamiento runtime para campañas
```

## Directorios Clave

*   **`models/`**: Clases Python que representan documentos MongoDB y CRUD.
*   **`routes/`**: Lógica de aplicación separada por módulos (Auth, API, Web UI).
*   **`plugins/actions/`**: Añade nuevas capacidades al sistema.
*   **`utils/`**: Núcleo para tareas complejas como `campain_executor.py` (runner).
