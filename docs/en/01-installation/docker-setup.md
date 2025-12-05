# Docker Installation

Running TestGyver with Docker is the easiest way to get started, ensuring all dependencies are isolated.

## Building the Image

1.  Navigate to the project root:
    ```bash
    cd app_test
    ```

2.  Build the Docker image:
    ```bash
    docker build -t testgyver:latest .
    ```

## Running with Docker Compose (Recommended)

Create a `docker-compose.yml` file in the root directory to orchestrate the application and the MongoDB database.

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

Start the stack:
```bash
docker-compose up -d
```

The application will be available at `http://localhost:5000`.

## Running Manually with Docker

If you prefer running containers individually:

1.  Start MongoDB:
    ```bash
    docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=mypass mongo:6.0
    ```

2.  Run the application. To connect to a MongoDB instance running on your host machine (localhost), use the following command:
    ```bash
    docker run --rm \
      -p 5000:5000 \
      --add-host=host.docker.internal:host-gateway \
      -e MONGO_HOST=host.docker.internal \
      testgyver:latest
    ```
