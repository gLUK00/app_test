# Frontend-Entwicklung

Das Frontend nutzt einfache Web-Technologien für Wartbarkeit.

## Technologien

*   **HTML/Templates**: Jinja2
*   **CSS**: Bootstrap 5.3 (lokal in `static/vendor`)
*   **JavaScript**: Vanilla JS + etwas jQuery (Legacy)
*   **Icons**: FontAwesome 6.4 (lokal)

## Asset-Management

Kein komplexer Build (kein Webpack/Vite). Assets kommen direkt aus `static/`.

### Lokale Vendor Libraries
Keine CDNs, alles liegt in `static/vendor/`.

## Dynamische Interaktion

### Modals & Forms
Bootstrap Modals für "Add Variable" oder "Upload File". JS macht AJAX-Calls zum API.

### Echtzeit-Updates
**Socket.IO** aktualisiert ohne Reload.
*   **Kampagnenlauf**: Fortschritt/Logs live.
*   **Dateien**: Liste aktualisiert sich bei Upload/Delete.

## Neue Seite hinzufügen

1.  Route in `routes/web_routes.py` anlegen.
2.  Template in `templates/` erstellen (erbt `base.html`).
3.  Link in der Navigation ergänzen.
