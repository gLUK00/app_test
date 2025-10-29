# Guide d'utilisation du Docker Compose de test

Ce fichier `test-docker-compose.yml` permet de démarrer un environnement de test complet pour tester toutes les actions disponibles dans l'application TestGyver.

## Services disponibles

### 1. Serveur FTP (`ftp-server`)
- **Port**: 21 (+ ports passifs 30000-30009)
- **Credentials**: 
  - Utilisateur: `testuser`
  - Mot de passe: `testpass`
- **Utilisation**: Tester les actions FTP (GET, PUT, DELETE, LIST)

### 2. Serveur SFTP (`sftp-server`)
- **Port**: 2222
- **Credentials**:
  - Utilisateur: `testuser`
  - Mot de passe: `testpass`
- **Répertoire**: `/upload`
- **Utilisation**: Tester les actions SFTP (GET, PUT, DELETE, LIST)

### 3. Serveur WebDAV (`webdav-server`)
- **Port**: 8080
- **URL**: `http://localhost:8080`
- **Credentials**:
  - Utilisateur: `testuser`
  - Mot de passe: `testpass`
- **Utilisation**: Tester les actions WebDAV (GET, PUT, DELETE, MKCOL)

### 4. API HTTP de test (`http-api`)
- **Port**: 8082
- **URL**: `http://localhost:8082`
- **Description**: HTTPBin - API de test HTTP complète
- **Utilisation**: Tester les actions HTTP (GET, POST, PUT, DELETE)
- **Endpoints utiles**:
  - `http://localhost:8082/get` - Test GET
  - `http://localhost:8082/post` - Test POST
  - `http://localhost:8082/put` - Test PUT
  - `http://localhost:8082/delete` - Test DELETE
  - `http://localhost:8082/status/200` - Retourne un status code spécifique

### 5. Serveur SSH (`ssh-server`)
- **Port**: 2223
- **Credentials**:
  - Utilisateur: `testuser`
  - Mot de passe: `testpass`
- **Utilisation**: Tester les actions SSH (exécution de commandes)

## Démarrage de l'environnement

### Démarrer tous les services
```bash
cd init
docker-compose -f test-docker-compose.yml up -d
```

### Vérifier l'état des services
```bash
docker-compose -f test-docker-compose.yml ps
```

### Voir les logs
```bash
# Tous les services
docker-compose -f test-docker-compose.yml logs -f

# Un service spécifique
docker-compose -f test-docker-compose.yml logs -f ftp-server
```

### Arrêter les services
```bash
docker-compose -f test-docker-compose.yml down
```

### Arrêter et supprimer les volumes
```bash
docker-compose -f test-docker-compose.yml down -v
```

## Exemples de configuration pour les tests

### Action FTP
```json
{
  "method": "LIST",
  "host": "localhost",
  "port": 21,
  "username": "testuser",
  "password": "testpass",
  "remote_path": "/"
}
```

### Action SFTP
```json
{
  "method": "LIST",
  "host": "localhost",
  "port": 2222,
  "username": "testuser",
  "password": "testpass",
  "remote_path": "/upload"
}
```

### Action WebDAV
```json
{
  "method": "GET",
  "url": "http://localhost:8080/",
  "username": "testuser",
  "password": "testpass"
}
```

### Action HTTP
```json
{
  "method": "GET",
  "url": "http://localhost:8082/get",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

### Action SSH
```json
{
  "host": "localhost",
  "port": 2223,
  "username": "testuser",
  "password": "testpass",
  "command": "ls -la"
}
```

## Dépannage

### Les services ne démarrent pas
- Vérifiez que Docker est installé et en cours d'exécution
- Vérifiez que les ports ne sont pas déjà utilisés
- Consultez les logs: `docker-compose -f test-docker-compose.yml logs`

### Problèmes de connexion
- Assurez-vous que les services sont bien démarrés: `docker-compose -f test-docker-compose.yml ps`
- Vérifiez que les ports sont correctement mappés
- Testez la connectivité: `telnet localhost <port>`

### Réinitialiser l'environnement
```bash
docker-compose -f test-docker-compose.yml down -v
docker-compose -f test-docker-compose.yml up -d
```

## Notes importantes

- Tous les services utilisent les mêmes credentials par défaut: `testuser` / `testpass`
- Les données sont stockées dans des volumes Docker pour persister entre les redémarrages
- Ces services sont destinés **uniquement aux tests** et ne doivent pas être utilisés en production
- Le réseau `test-network` permet aux conteneurs de communiquer entre eux si nécessaire
