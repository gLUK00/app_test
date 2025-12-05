# Instalación con Docker

Ejecutar TestGyver con Docker es la forma más sencilla de empezar, asegurando que todas las dependencias estén aisladas.

## Construir la Imagen

1.  Navega a la raíz del proyecto:
    ```bash
    cd app_test
    ```

2.  Construye la imagen de Docker:
    ```bash
    docker build -t testgyver:latest .
    ```

## Ejecución con Docker Compose (Recomendado)

Crea un archivo `docker-compose.yml` en el directorio raíz para orquestar la aplicación y la base de datos MongoDB.

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

Inicia la pila:
```bash
docker-compose up -d
```

La aplicación estará disponible en `http://localhost:5000`.

## Ejecución Manual con Docker

Si prefieres ejecutar los contenedores individualmente:

1.  Inicia MongoDB:
    ```bash
    docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=mypass mongo:6.0
    ```

2.  Ejecuta la aplicación. Para conectarte a una instancia de MongoDB que se ejecuta en tu máquina host (localhost), usa el siguiente comando:
    ```bash
    docker run --rm \
      -p 5000:5000 \
      --add-host=host.docker.internal:host-gateway \
      -e MONGO_HOST=host.docker.internal \
      testgyver:latest
    ```
