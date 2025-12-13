# Docker-Installation

Das Ausführen von TestGyver mit Docker ist der einfachste Weg, um zu beginnen, da alle Abhängigkeiten isoliert sind.

## Erstellen des Images

1.  Navigieren Sie zum Projektstammverzeichnis:
    ```bash
    cd app_test
    ```

2.  Erstellen Sie das Docker-Image:
    ```bash
    docker build -t testgyver:latest .
    ```

## Ausführen mit Docker Compose (Empfohlen)

Erstellen Sie eine `docker-compose.yml`-Datei im Stammverzeichnis, um die Anwendung und die MongoDB-Datenbank zu orchestrieren.

```yaml
version: '3.8'

services:
  mongo:
    image: mongo:6.0
    container_name: testgyver-mongo
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: mypass
    volumes:
      - mongo_data:/data/db

  app:
    image: testgyver:latest
    container_name: testgyver-app
    build: .
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
    depends_on:
      - mongo
    volumes:
      - ./configuration.json:/app/configuration.json
      - ./workdir:/app/workdir

volumes:
  mongo_data:
```

Starten Sie den Stack:
```bash
docker-compose up -d
```

Die Anwendung ist unter `http://localhost:8080` verfügbar.

## Manuelles Ausführen mit Docker

Wenn Sie Container lieber einzeln ausführen möchten:

1.  Starten Sie MongoDB:
    ```bash
    docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=mypass mongo:6.0
    ```

2.  Starten Sie die Anwendung. Um eine Verbindung zu einer MongoDB-Instanz herzustellen, die auf Ihrem Host-Rechner (localhost) läuft, verwenden Sie den folgenden Befehl:
    ```bash
    docker run --rm \
      -p 8080:8080 \
      --add-host=host.docker.internal:host-gateway \
      -e MONGO_HOST=host.docker.internal \
      testgyver:latest
    ```
