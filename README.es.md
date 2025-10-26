# TestGyver

## Elige tu idioma
- [Français](README.md)
- [English](README.en.md)
- Español (por defecto en este archivo)
- [Deutsch](README.de.md)
- [Italiano](README.it.md)

## Descripción general
TestGyver es una plataforma de pruebas web multi-entorno pensada para orquestar, ejecutar y documentar campañas complejas. Inspirada en la creatividad de MacGyver, combina un sistema flexible de acciones con informes detallados y módulos de administración.

## Funcionalidades clave
- Flujo de autenticación con JWT y página de inicio de sesión dedicada (`/`).
- Panel de control posterior al login (`/dashboard`) con listado de campañas y accesos rápidos para administradores.
- Gestión completa de campañas, pruebas y reportes de ejecución.
- Módulos administrativos para gestionar usuarios y variables por entorno.
- Catálogo de acciones extensible (HTTPRequest, WebDAV, FTP, SFTP, SSH, etc.) basado en máscaras JSON.
- Documentación interactiva de la API disponible en `/swagger`.

## Pila tecnológica
- **Backend / Frontend:** Flask, Jinja2, Bootstrap, FontAwesome.
- **Base de datos:** MongoDB (`users`, `variables`, `campains`, `tests`, `rapports`).
- **Persistencia:** PyMongo.
- **Seguridad:** JWT con expiración configurable y control de roles.
- **Configuración:** `configuration.json` (MongoDB, app, paginación, seguridad, versión).
- **Recursos estáticos:** Servidos desde `static/` con archivos CDN locales.

## Requisitos
- Python 3.11 o superior
- MongoDB 6.x o compatible
- `pip` y un gestor de entornos virtuales
- Opcional: Node.js para ampliar los assets front-end

## Instalación
1. Clona el repositorio:
   ```bash
   git clone <url-del-repo> && cd app_test
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración
1. Crea `configuration.json` (o copia el ejemplo):
   ```json
   {
       "mongo": {
           "user": "root",
           "pass": "mypass",
           "host": "localhost",
           "port": "27017",
           "bdd": "testGyver"
       },
       "jwt_secret": "change-me",
       "app": {
           "debug": true,
           "port": 5000
       },
       "pagination": {
           "page_size": 20
       },
       "security": {
           "token_expiration_minutes": 60
       },
       "version": "1.0.0"
   }
   ```
2. Añade un archivo `.env` (ignorado por Git) para credenciales sensibles si lo necesitas.

## Ejecución local
1. Inicia MongoDB y confirma las credenciales.
2. Exporta las variables de entorno de Flask:
   ```bash
   export FLASK_APP=app
   export FLASK_ENV=development
   ```
3. Arranca la aplicación:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```
4. Abre `http://localhost:5000` en tu navegador.

## Scripts útiles
- `start.sh`: script estándar de inicio (también usado por Docker). Asegúrate de hacerlo ejecutable con `chmod +x start.sh`.
- CLI de `flask`: tareas de mantenimiento, creación de administradores, etc.

## Flujo con Docker
1. Construye la imagen:
   ```bash
   docker build -t testgyver:latest .
   ```
2. Ejecuta el contenedor con tus variables:
   ```bash
   docker run -p 5000:5000 --env-file .env testgyver:latest
   ```
3. Monta tu `configuration.json` si prefieres externalizarlo:
   ```bash
   docker run -p 5000:5000 \
       -v $(pwd)/configuration.json:/app/configuration.json \
       --env-file .env \
       testgyver:latest
   ```

## Depuración en VS Code
1. Instala la extensión de Python y selecciona el intérprete.
2. Abre el proyecto en VS Code.
3. Elige **TestGyver: Flask Debug** en la vista Run and Debug.
4. Coloca breakpoints y lanza la depuración.

## Modelo de datos
- `users`: identidad, contraseña hasheada y rol (`admin`, `user`).
- `variables`: pares clave/valor agrupados por entorno (`filiere`).
- `campains`: metadatos de la campaña (autor, descripción, fechas).
- `tests`: acciones ordenadas vinculadas a una campaña.
- `rapports`: resultados de ejecución, estado por prueba y logs.

## API principal
- `POST /api/login`, `POST /api/logout` para el ciclo JWT.
- Endpoints CRUD para `/api/users`, `/api/campains`, `/api/tests`, `/api/variables`, `/api/rapports`.
- Documentación interactiva en `/swagger`.

## Ampliar acciones
Cada clase dentro de `plugins/actions` extiende `ActionBase` y debe:
- proporcionar una máscara JSON con los campos configurables;
- implementar `execute(ActionContext)` con la lógica específica;
- devolver las trazas para los reportes.

## Próximos pasos
- Crea acciones personalizadas extendiendo `ActionBase`.
- Integra TestGyver con pipelines CI/CD para planificar campañas.
- Añade canales de notificación (Slack, correo, Teams) para compartir reportes.

## Soporte
Abre un issue en GitHub o contacta con el equipo TestGyver para dudas y sugerencias.
