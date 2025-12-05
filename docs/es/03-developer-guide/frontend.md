# Desarrollo Frontend

El frontend usa tecnologías web estándar para mantener la mantenibilidad.

## Tecnologías

*   **HTML/Plantillas**: Jinja2.
*   **CSS**: Bootstrap 5.3 (copia local en `static/vendor`).
*   **JavaScript**: Vanilla JS + algo de jQuery (legado).
*   **Iconos**: FontAwesome 6.4 (copia local).

## Gestión de Assets

No usamos build complejo (Webpack/Vite). Todos los assets se sirven desde `static/`.

### Librerías Vendor Locales
Para privacidad y trabajo offline, no usamos CDNs. Todo está en `static/vendor/`.

## Interacciones Dinámicas

### Modals y Formularios
Bootstrap Modals para "Add Variable" o "Upload File". JavaScript hace las peticiones AJAX al API.

### Actualizaciones en Tiempo Real
Usamos **Socket.IO** para actualizar sin recargar.
*   **Ejecución de Campañas**: Barras de progreso y logs en vivo.
*   **Gestión de Ficheros**: Lista se actualiza al subir/borrar.

## Añadir una Página Nueva

1.  Crea una ruta en `routes/web_routes.py`.
2.  Crea una plantilla en `templates/` extendiendo `base.html`.
3.  Añade un enlace en la navegación.
