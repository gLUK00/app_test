# Sviluppo Frontend

Frontend semplice per mantenibilità.

## Tecnologie

*   **HTML/Template**: Jinja2
*   **CSS**: Bootstrap 5.3 (locale `static/vendor`)
*   **JavaScript**: Vanilla JS + jQuery (legacy)
*   **Icone**: FontAwesome 6.4 (locale)

## Asset

Nessun build complesso (no Webpack/Vite). Asset serviti da `static/`.

### Librerie Vendor Locali
Nessun CDN, tutto in `static/vendor/`.

## Interazioni Dinamiche

### Modali & Form
Bootstrap Modals per "Add Variable" o "Upload File". JS fa chiamate AJAX all'API.

### Aggiornamenti Real-time
**Socket.IO** aggiorna senza refresh.
*   **Esecuzione Campagne**: progressi/log live.
*   **File**: lista aggiornata su upload/delete.

## Aggiungere una Nuova Pagina

1.  Rotta in `routes/web_routes.py`.
2.  Template in `templates/` estendendo `base.html`.
3.  Link in navigazione.
