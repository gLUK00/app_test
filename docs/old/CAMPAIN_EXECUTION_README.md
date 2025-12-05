# Système d'exécution de campagnes en temps réel

## Vue d'ensemble

Ce document décrit le système d'exécution de campagnes de tests avec suivi en temps réel via WebSockets.

## Architecture

### Composants principaux

1. **CampainExecutor** (`utils/campain_executor.py`)
   - Gère l'exécution des campagnes en arrière-plan
   - Exécute les tests de manière séquentielle
   - Émet des événements WebSocket pour la progression

2. **Modèle Rapport** (étendu)
   - Nouveaux champs:
     - `status`: pending, running, completed, failed
     - `progress`: pourcentage de progression (0-100)
     - `stopOnFailure`: arrêter au premier échec

3. **WebSocket avec Flask-SocketIO**
   - Communication bidirectionnelle en temps réel
   - Événements émis pendant l'exécution

## Flux d'exécution

### 1. Lancement d'une campagne

**Interface utilisateur** (`campain_details.html`):
- Bouton "Exécuter la campagne"
- Ouvre une modale avec:
  - Nom du rapport (auto-généré: "Mois Année")
  - Sélection de l'environnement (filière)
  - Option "Arrêter au premier échec"
  - Boutons "Lancer" et "Annuler"

**Validation**:
- Le nom du rapport est obligatoire et doit être unique
- L'environnement est obligatoire
- Si le nom existe déjà, un suffixe numérique est ajouté

### 2. Exécution en arrière-plan

**Endpoint**: `POST /api/rapports/execute`

```json
{
  "campain_id": "...",
  "name": "Octobre 2025",
  "filiere": "PRODUCTION",
  "stop_on_failure": false
}
```

**Processus**:
1. Création d'un rapport avec status="pending"
2. Récupération des tests de la campagne
3. Lancement d'un thread d'exécution
4. Retour immédiat de l'ID du rapport

### 3. Exécution des tests

Pour chaque test de la campagne:

1. **Préparation**:
   - Chargement des variables de l'environnement
   - Initialisation des variables de collection (test_id, campain_id)
   - Initialisation des variables de sortie du test

2. **Exécution**:
   - Pour chaque action du test:
     - Résolution des variables dans les paramètres
     - Chargement du plugin d'action
     - Exécution de l'action
     - Capture des variables de sortie
     - Génération de logs

3. **Gestion des échecs**:
   - Si `stop_on_failure` est activé et qu'un test échoue:
     - Les tests restants sont marqués comme "skipped"
     - L'exécution s'arrête

### 4. Événements WebSocket

**Événements émis**:

- `campain_started`: Début de l'exécution
  ```json
  {
    "rapport_id": "...",
    "campain_id": "..."
  }
  ```

- `test_started`: Début d'un test
  ```json
  {
    "rapport_id": "...",
    "test_id": "..."
  }
  ```

- `test_completed`: Fin d'un test
  ```json
  {
    "rapport_id": "...",
    "test_id": "...",
    "status": "passed|failed|skipped",
    "logs": "..."
  }
  ```

- `campain_progress`: Mise à jour de la progression
  ```json
  {
    "rapport_id": "...",
    "progress": 75
  }
  ```

- `campain_completed`: Fin de l'exécution
  ```json
  {
    "rapport_id": "...",
    "status": "completed|failed",
    "result": "success|failure"
  }
  ```

- `campain_error`: Erreur lors de l'exécution
  ```json
  {
    "rapport_id": "...",
    "error": "..."
  }
  ```

## Interface utilisateur

### Page de détails de campagne

**Affichage des rapports** (`campain_details.html`):
- Liste des rapports avec:
  - Nom du rapport
  - Date d'exécution
  - Environnement (badge)
  - Statut (badge coloré avec icône)
  - Progression (barre de progression)
  - Bouton "Voir"

**Statuts possibles**:
- **Pending** (gris): En attente
- **Running** (bleu): En cours d'exécution
- **Completed** (vert): Terminé avec succès
- **Failed** (rouge): Terminé avec des échecs

### Page de détails du rapport

**Vue d'ensemble** (`rapport_details.html`):
- Informations générales:
  - Nom du rapport
  - Environnement
  - Date de création
  - Statut
  - Barre de progression

**Liste des tests**:
- Accordéon avec un élément par test
- Pour chaque test:
  - Icône et badge de statut
  - Logs d'exécution en temps réel
  - Défilement automatique des logs

**Indicateur "Live"**:
- Affiché pendant l'exécution
- Point rouge clignotant
- Masqué quand l'exécution est terminée

**Mise à jour en temps réel**:
- Connexion WebSocket automatique
- Mise à jour automatique des statuts
- Mise à jour automatique de la progression
- Ajout automatique des logs

## Résolution des variables

Le système supporte trois types de variables:

### 1. Variables TestGyver
Format: `{{variable_name}}`
- Stockées dans la collection `variables`
- Filtrées par environnement (filière)
- Exemple: `{{api_url}}` → `https://api.example.com`

### 2. Variables de test
Format: `{{app.variable_name}}`
- Définies dans le test
- Alimentées par les variables de sortie des actions
- Exemple: `{{app.user_id}}` → valeur retournée par une action

### 3. Variables de collection
Format: `{{test.variable_name}}`
- Variables système:
  - `{{test.test_id}}`: ID du test en cours
  - `{{test.campain_id}}`: ID de la campagne

## Exemples d'utilisation

### Exemple 1: Exécution simple

```javascript
// Lancer une campagne
const result = await API.post('/api/rapports/execute', {
  campain_id: '507f1f77bcf86cd799439011',
  name: 'Octobre 2025',
  filiere: 'PRODUCTION',
  stop_on_failure: false
});

// result.rapport_id contient l'ID du rapport créé
```

### Exemple 2: Écoute des événements WebSocket

```javascript
const socket = io();

socket.on('connect', () => {
  socket.emit('join_rapport', { rapport_id: rapportId });
});

socket.on('test_completed', (data) => {
  console.log(`Test ${data.test_id}: ${data.status}`);
  console.log('Logs:', data.logs);
});

socket.on('campain_completed', (data) => {
  console.log(`Campagne terminée: ${data.status}`);
});
```

### Exemple 3: Test avec variables

```json
{
  "type": "HTTPRequestAction",
  "value": {
    "method": "POST",
    "url": "{{api_url}}/users",
    "headers": {
      "Authorization": "Bearer {{api_token}}"
    },
    "body": {
      "test_id": "{{test.test_id}}",
      "previous_user_id": "{{app.user_id}}"
    }
  }
}
```

## Gestion des erreurs

### Erreurs de validation
- Nom de rapport manquant → HTTP 400
- Environnement manquant → HTTP 400
- Nom de rapport non unique → HTTP 400
- Aucun test dans la campagne → HTTP 400

### Erreurs d'exécution
- Erreur lors de l'exécution d'une action → Test marqué "failed"
- Erreur système → Rapport marqué "failed", événement `campain_error`

### Stratégie "Arrêter au premier échec"
- Si activée: dès qu'un test échoue, les tests restants sont ignorés
- Tests ignorés: status="skipped", logs="Test ignoré après un échec précédent"

## API Endpoints

### POST /api/rapports/execute
Lance l'exécution d'une campagne.

**Corps de la requête**:
```json
{
  "campain_id": "string (required)",
  "name": "string (required)",
  "filiere": "string (required)",
  "stop_on_failure": "boolean (optional, default: false)"
}
```

**Réponse (201)**:
```json
{
  "message": "Exécution de la campagne lancée",
  "rapport_id": "..."
}
```

### GET /api/rapports/generate-name
Génère un nom unique pour un rapport.

**Réponse (200)**:
```json
{
  "name": "Octobre 2025"
}
```

Si le nom existe déjà:
```json
{
  "name": "Octobre 2025 (1)"
}
```

### GET /api/rapports/filieres
Récupère la liste des environnements disponibles.

**Réponse (200)**:
```json
{
  "filieres": ["DEV", "TEST", "PRODUCTION"]
}
```

### GET /api/rapports/:id
Récupère les détails d'un rapport (incluant status et progress).

**Réponse (200)**:
```json
{
  "_id": "...",
  "campainId": "...",
  "dateCreated": "2025-10-30T10:00:00Z",
  "details": "Octobre 2025",
  "filiere": "PRODUCTION",
  "status": "running",
  "progress": 45,
  "stopOnFailure": false,
  "tests": [
    {
      "testId": "...",
      "status": "passed",
      "logs": "..."
    }
  ]
}
```

## Dépendances

- **Flask-SocketIO**: Gestion des WebSockets
- **python-socketio**: Client/serveur Socket.IO
- **eventlet**: Serveur WSGI asynchrone pour SocketIO

Installation:
```bash
pip install -r requirements.txt
```

## Configuration

Dans `app.py`:
```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
```

Lancement de l'application:
```python
socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

## Tests

Pour tester manuellement:

1. Créer une campagne avec plusieurs tests
2. Ajouter des variables pour l'environnement sélectionné
3. Lancer l'exécution depuis la page de détails de la campagne
4. Observer la progression en temps réel
5. Vérifier les logs dans la page de détails du rapport

## Notes techniques

- L'exécution se fait dans un thread séparé pour ne pas bloquer l'application
- Les threads sont en mode daemon pour s'arrêter avec l'application
- Les événements WebSocket sont émis après chaque opération importante
- La progression est calculée en pourcentage: (tests_exécutés / total_tests) * 100
- Les logs sont formatés avec timestamp: `[HH:MM:SS] Message`
