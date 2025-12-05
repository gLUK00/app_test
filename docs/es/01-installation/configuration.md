# Configuración

La aplicación se configura mediante un archivo `configuration.json` ubicado en la raíz.

## Estructura

```json
{
    "mongo": {
        "user": "root",
        "pass": "mypass",
        "host": "localhost",
        "port": "27017",
        "bdd": "testGyver",
        "prefix": "mgv_",
        "soft_delete": true
    },
    "jwt_secret": "your-secret-key",
    "app": {
        "debug": true,
        "port": 5000,
        "host": "0.0.0.0"
    },
    "pagination": {
        "page_size": 20,
        "max_page_size": 100
    },
    "security": {
        "token_expiration_minutes": 60,
        "password_min_length": 8
    },
    "workdir": "./workdir",
    "version": "1.0.0"
}
```

## Detalle de Parámetros

### Mongo
*   **user**: Usuario de MongoDB.
*   **pass**: Contraseña de MongoDB.
*   **host**: Host de la base (ej: `localhost` o `mongo` en Docker).
*   **port**: Puerto de la base (por defecto `27017`).
*   **bdd**: Nombre de la base de datos a usar.
*   **prefix**: Prefijo para las colecciones (ej: `mgv_users`).
*   **soft_delete**: Si es true, los ítems se marcan como eliminados en lugar de borrarse.

### Seguridad
*   **jwt_secret**: Cadena larga y aleatoria para firmar JWT. **Cámbiala en producción**.
*   **token_expiration_minutes**: Duración de la sesión en minutos.
*   **password_min_length**: Mínimo de caracteres para contraseñas.

### App
*   **debug**: Activa modo debug de Flask (auto-reload). Pon `false` en producción.
*   **port**: Puerto donde escucha la app.
*   **host**: Interfaz de enlace (`0.0.0.0` para todas).

### Workdir
*   **workdir**: Ruta al directorio donde se almacenan archivos de campañas y datos temporales.
