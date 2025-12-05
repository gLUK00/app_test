# Installazione Docker

Eseguire TestGyver con Docker è il modo più semplice per iniziare, garantendo che tutte le dipendenze siano isolate.

## Costruire l'Immagine

1.  Naviga alla root del progetto:
    ```bash
    cd app_test
    ```

2.  Costruisci l'immagine Docker:
    ```bash
    docker build -t testgyver:latest .
    ```

## Esecuzione con Docker Compose (Consigliato)

Crea un file `docker-compose.yml` nella directory root per orchestrare l'applicazione e il database MongoDB.

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
      - "5000:5000"
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

Avvia lo stack:
```bash
docker-compose up -d
```

L'applicazione sarà disponibile su `http://localhost:5000`.

## Esecuzione Manuale con Docker

Se preferisci eseguire i container individualmente:

1.  Avvia MongoDB:
    ```bash
    docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=mypass mongo:6.0
    ```

2.  Esegui l'applicazione. Per connetterti a un'istanza MongoDB in esecuzione sulla tua macchina host (localhost), usa il seguente comando:
    ```bash
    docker run --rm \
      -p 5000:5000 \
      --add-host=host.docker.internal:host-gateway \
      -e MONGO_HOST=host.docker.internal \
      testgyver:latest
    ```
