# Installation Docker

Exécuter TestGyver avec Docker est la méthode la plus simple pour démarrer, garantissant l'isolation de toutes les dépendances.

## Construire l'Image

1.  Naviguez vers la racine du projet :
    ```bash
    cd app_test
    ```

2.  Construisez l'image Docker :
    ```bash
    docker build -t testgyver:latest .
    ```

## Exécution avec Docker Compose (Recommandé)

Créez un fichier `docker-compose.yml` à la racine pour orchestrer l'application et la base de données MongoDB.

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

Démarrez la stack :
```bash
docker-compose up -d
```

L'application sera disponible sur `http://localhost:8080`.

## Exécution Manuelle avec Docker

Si vous préférez lancer les conteneurs individuellement :

1.  Démarrez MongoDB :
    ```bash
    docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=root -e MONGO_INITDB_ROOT_PASSWORD=mypass mongo:6.0
    ```

2.  Lancez l'application. Pour vous connecter à une instance MongoDB s'exécutant sur votre machine hôte (localhost), utilisez la commande suivante :
    ```bash
    docker run --rm \
      -p 8080:8080 \
      --add-host=host.docker.internal:host-gateway \
      -e MONGO_HOST=host.docker.internal \
      testgyver:latest
    ```
