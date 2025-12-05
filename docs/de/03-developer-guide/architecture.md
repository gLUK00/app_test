# Architektur-Übersicht

TestGyver ist eine monolithische Web-App mit modularem Plugin-System.

## High-Level-Diagramm

```mermaid
graph TD
    Client[Web Browser] <-->|HTTP/WebSocket| Flask[Flask Application]
    Flask <-->|PyMongo| Mongo[(MongoDB)]
    Flask -->|Load| Plugins[Action Plugins]
    Flask -->|Execute| Executor[Campain Executor]
    Executor --> Plugins
    Executor -->|Update| Mongo
    Executor -->|Emit| SocketIO[Socket.IO]
    SocketIO -->|Push| Client
```

## Kernkomponenten

### 1. Flask-App (`app.py`)
Entry Point. Initialisiert:
*   DB-Verbindung
*   Auth (JWT)
*   Blueprints (Routes)
*   SocketIO
*   Plugin-Manager

### 2. Daten-Layer (`models/`)
Abstraktion über MongoDB via PyMongo.
*   **Users**, **Variables**, **Campaigns/Tests**, **Reports**

### 3. Plugins (`plugins/`)
Dynamisches Laden von Aktionen.
*   **PluginManager**: Scan & Load
*   **ActionBase**: Abstrakte Basis

### 4. Execution Engine (`utils/campain_executor.py`)
Background-Thread/Prozess.
*   Läuft Tests/Aktionen
*   Variablenauflösung
*   Logs/Timings
*   DB-Updates & WebSocket-Events

### 5. Frontend
*   Jinja2, Bootstrap 5, jQuery/Vanilla JS
*   Socket.IO Client für Echtzeit
