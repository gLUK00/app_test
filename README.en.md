# TestGyver

## Choose Your Language
- [Français](README.md)
- English (default for this file)
- [Español](README.es.md)
- [Deutsch](README.de.md)
- [Italiano](README.it.md)

## Overview
TestGyver is a multi-environment web testing platform designed to orchestrate, execute, and document complex test campaigns. Inspired by the ingenuity of MacGyver, it blends a flexible action plugin system with rich reporting and administration features.

## Key Features
- JWT-secured authentication flow with a dedicated login page (`/`).
- Post-login dashboard (`/dashboard`) listing all campaigns and shortcuts for administrators.
- End-to-end management for campaigns, tests, and execution reports.
- Administrator modules to maintain users and environment-specific variables.
- Extensible action catalog (HTTPRequest, WebDAV, FTP, SFTP, SSH, etc.) backed by JSON-driven input masks.
- Swagger-powered API documentation exposed at `/swagger`.

## Tech Stack
- **Backend / Frontend:** Flask, Jinja2, Bootstrap, FontAwesome.
- **Database:** MongoDB (`users`, `variables`, `campains`, `tests`, `rapports`).
- **Persistence:** PyMongo.
- **Security:** JWT with configurable token expiration and role-based access control.
- **Configuration:** `configuration.json` (MongoDB, app, pagination, security, versioning).
- **Static Assets:** Served from `static/` with self-hosted CDN files.

## Requirements
- Python 3.11+
- MongoDB 6.x or compatible
- `pip` and a virtual environment manager (`venv`, `virtualenv`, etc.)
- Optional: Node.js if you plan to extend front-end assets

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url> && cd app_test
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
1. Create `configuration.json` (or copy from a template):
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
2. Add a `.env` file (ignored by Git) to store sensitive environment variables if needed.

## Running Locally
1. Start MongoDB and verify credentials match your configuration.
2. Export Flask environment variables:
   ```bash
   export FLASK_APP=app
   export FLASK_ENV=development
   ```
3. Launch the app:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```
4. Open `http://localhost:5000` in your browser.

## Helpful Scripts
- `start.sh`: normalized entry script (also used inside the Docker image). Make it executable with `chmod +x start.sh`.
- `flask` CLI: manage admin users, seed data, or custom maintenance tasks.

## Docker Workflow
1. Build the image:
   ```bash
   docker build -t testgyver:latest .
   ```
2. Run the container with your environment file:
   ```bash
   docker run -p 5000:5000 --env-file .env testgyver:latest
   ```
3. Optionally mount your local `configuration.json`:
   ```bash
   docker run -p 5000:5000 \
       -v $(pwd)/configuration.json:/app/configuration.json \
       --env-file .env \
       testgyver:latest
   ```

## VS Code Debugging
1. Install the Python extension and select the correct interpreter.
2. Open the repository in VS Code.
3. Choose the **TestGyver: Flask Debug** configuration in the Run and Debug panel.
4. Set breakpoints where needed and start debugging.

## Data Model
- `users`: identity information, hashed password, role (`admin`, `user`).
- `variables`: key/value pairs grouped by environment (`filiere`).
- `campains`: campaign metadata (creator, description, timestamps).
- `tests`: ordered actions linked to a campaign.
- `rapports`: execution outcomes, per-test status, and logs.

## Main API Surface
- `POST /api/login`, `POST /api/logout` for JWT lifecycle.
- CRUD endpoints for `/api/users`, `/api/campains`, `/api/tests`, `/api/variables`, `/api/rapports`.
- Interactive documentation available at `/swagger`.

## Extending Actions
Each action class inside `plugins/actions` extends `ActionBase` and must:
- provide a JSON input mask describing configurable fields;
- implement `execute(ActionContext)` to run its logic;
- return execution traces that feed the reporting module.

## Next Steps
- Create new actions by subclassing `ActionBase`.
- Connect TestGyver to CI/CD pipelines (GitHub Actions, Jenkins, GitLab) to schedule campaigns.
- Integrate notification channels (Slack, email, Teams) for report dissemination.

## Support
Open a GitHub issue or contact the TestGyver team for questions and feature requests.
