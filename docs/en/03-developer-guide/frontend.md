# Frontend Development

The frontend is built using standard web technologies, kept simple to ensure maintainability.

## Technologies

*   **HTML/Templates**: Jinja2 (Python templating engine).
*   **CSS**: Bootstrap 5.3 (local copy in `static/vendor`).
*   **JavaScript**: Vanilla JS + some jQuery (legacy).
*   **Icons**: FontAwesome 6.4 (local copy).

## Asset Management

We do not use a complex build step (Webpack/Vite). All assets are served directly from the `static/` directory.

### Local Vendor Libraries
To respect privacy and ensure offline capability, we do not use CDNs. All libraries are stored in `static/vendor/`.

## Dynamic Interactions

### Modals & Forms
We use Bootstrap Modals for interactions like "Add Variable" or "Upload File". JavaScript handles the AJAX requests to the API.

### Real-time Updates
We use **Socket.IO** to update the UI without reloading.
*   **Campaign Execution**: Progress bars and logs update live.
*   **File Management**: The file list updates automatically when a file is uploaded/deleted.

## Adding a New Page

1.  Create a route in `routes/web_routes.py`.
2.  Create a template in `templates/` extending `base.html`.
3.  Add a link in the navigation (in `base.html` or specific view).
