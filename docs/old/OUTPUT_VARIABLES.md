# Variables de Sortie des Actions

## Vue d'ensemble

Le système de variables de sortie permet aux actions de partager des données entre elles lors de l'exécution d'un test. Chaque action peut définir une ou plusieurs variables de sortie qui pourront être utilisées par les actions suivantes dans le même test.

## Fonctionnement

### 1. Déclaration des variables de sortie

Chaque plugin d'action définit les variables de sortie qu'il peut produire via la méthode `get_output_variables()`. Cette méthode retourne une liste de dictionnaires décrivant chaque variable disponible.

**Exemple :**
```python
def get_output_variables(self):
    """Retourne la liste des variables de sortie pour les requêtes HTTP."""
    return [
        {
            "name": "http_status_code",
            "description": "Code de statut HTTP de la réponse (ex: 200, 404, 500)",
            "type": "number"
        },
        {
            "name": "http_response_body",
            "description": "Corps de la réponse HTTP",
            "type": "string"
        }
    ]
```

### 2. Configuration dans l'interface utilisateur

Lors de l'ajout ou de la modification d'une action dans un test :

1. **Sélection du type d'action** : L'utilisateur choisit le type d'action (HTTP, SSH, FTP, etc.)
2. **Configuration des paramètres** : L'utilisateur remplit les champs requis pour l'action
3. **Mapping des variables de sortie** : Une section spéciale affiche les variables de sortie disponibles
4. **Association aux variables du test** : L'utilisateur peut choisir de mapper chaque variable de sortie vers une variable du test

### 3. Exécution et propagation des valeurs

Lors de l'exécution de l'action, la méthode `execute()` retourne les valeurs réelles des variables de sortie dans un dictionnaire `output_variables` :

```python
output_vars = {
    "http_status_code": response.status_code,
    "http_response_body": response.text,
    "http_response_time": response.elapsed.total_seconds()
}

return self.get_result(result_data, output_vars)
```

Ces valeurs sont ensuite disponibles pour les actions suivantes via le mapping configuré.

## Variables de sortie par type d'action

### HTTP Request

| Variable | Description | Type |
|----------|-------------|------|
| `http_status_code` | Code de statut HTTP de la réponse | number |
| `http_response_body` | Corps de la réponse HTTP | string |
| `http_response_time` | Temps de réponse en secondes | number |
| `http_response_headers` | En-têtes de la réponse HTTP (JSON) | string |

### SSH

| Variable | Description | Type |
|----------|-------------|------|
| `ssh_exit_code` | Code de sortie de la commande SSH | number |
| `ssh_output` | Sortie standard de la commande | string |
| `ssh_error` | Sortie d'erreur de la commande | string |

### FTP

| Variable | Description | Type |
|----------|-------------|------|
| `ftp_file_content` | Contenu du fichier téléchargé (pour GET) | string |
| `ftp_file_size` | Taille du fichier en octets | number |
| `ftp_file_list` | Liste des fichiers (pour LIST) | string |
| `ftp_operation_success` | Indique si l'opération a réussi (true/false) | string |

### SFTP

| Variable | Description | Type |
|----------|-------------|------|
| `sftp_file_content` | Contenu du fichier téléchargé (pour GET) | string |
| `sftp_file_size` | Taille du fichier en octets | number |
| `sftp_file_list` | Liste des fichiers (pour LIST) | string |
| `sftp_operation_success` | Indique si l'opération a réussi (true/false) | string |

### WebDAV

| Variable | Description | Type |
|----------|-------------|------|
| `webdav_status_code` | Code de statut HTTP de la réponse WebDAV | number |
| `webdav_response_body` | Corps de la réponse WebDAV | string |
| `webdav_operation_success` | Indique si l'opération a réussi (true/false) | string |

## Exemple d'utilisation

### Scénario : Test d'API avec vérifications multiples

1. **Action 1 - HTTP Request** : Appeler une API pour créer une ressource
   - Variables de sortie mappées :
     - `http_status_code` → `creation_status`
     - `http_response_body` → `created_resource_id`

2. **Action 2 - HTTP Request** : Récupérer la ressource créée en utilisant l'ID
   - Paramètres utilisant les variables :
     - URL : `https://api.example.com/resources/${created_resource_id}`
   - Variables de sortie mappées :
     - `http_response_body` → `resource_details`

3. **Action 3 - SSH** : Vérifier la création côté serveur
   - Commande : `grep ${created_resource_id} /var/log/app.log`
   - Variables de sortie mappées :
     - `ssh_output` → `log_entry`

## Bonnes pratiques

### Nommage des variables

- Utilisez des noms descriptifs et explicites
- Préfixez les variables par le type d'action (ex: `http_`, `ssh_`, `ftp_`)
- Utilisez le snake_case pour la cohérence

### Gestion des données sensibles

- Évitez de mapper des mots de passe ou des clés API vers des variables
- Les variables de sortie sont stockées et peuvent être visibles dans les logs

### Organisation des tests

- Groupez les actions logiquement liées dans le même test
- Utilisez les variables de sortie pour créer des dépendances entre actions
- Documentez le flux de données dans la description du test

## API REST

### Récupérer toutes les variables de sortie

```
GET /api/actions/output-variables
```

**Réponse :**
```json
{
  "http": [
    {
      "name": "http_status_code",
      "description": "Code de statut HTTP de la réponse",
      "type": "number"
    }
  ],
  "ssh": [...]
}
```

### Récupérer les variables de sortie d'un type d'action

```
GET /api/actions/output-variables/{action_type}
```

**Exemple :**
```
GET /api/actions/output-variables/http
```

**Réponse :**
```json
{
  "type": "http",
  "output_variables": [
    {
      "name": "http_status_code",
      "description": "Code de statut HTTP de la réponse",
      "type": "number"
    },
    {
      "name": "http_response_body",
      "description": "Corps de la réponse HTTP",
      "type": "string"
    }
  ]
}
```

## Développement de nouveaux plugins

Consultez le [Guide de développement de plugins](PLUGIN_DEVELOPMENT_GUIDE.md) pour apprendre à implémenter des variables de sortie dans vos propres plugins d'actions.
