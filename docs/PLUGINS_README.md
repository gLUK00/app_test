# Système de Plugins TestGyver

## Vue d'ensemble

Le système de plugins de TestGyver permet d'étendre les fonctionnalités de l'application de manière modulaire et dynamique, sans nécessiter de modifications du code principal.

## Architecture

```
plugins/
├── plugin_base.py           # Classe de base pour tous les plugins
├── plugin_manager.py        # Gestionnaire générique de plugins
├── __init__.py              # Registre central des plugins
├── actions/                 # Plugins d'actions
│   ├── action_base.py
│   ├── __init__.py
│   ├── http_request_action.py
│   ├── ssh_action.py
│   ├── webdav_action.py
│   ├── ftp_action.py
│   └── sftp_action.py
├── reports/                 # Plugins de rapports
│   ├── report_base.py
│   ├── __init__.py
│   └── html_report_plugin.py (exemple)
└── auth/                    # Plugins d'authentification
    ├── auth_base.py
    ├── __init__.py
    └── local_auth_plugin.py (exemple)
```

## Fonctionnalités principales

### 1. Chargement automatique
Les plugins sont découverts et chargés automatiquement au démarrage de l'application. Il suffit de placer un nouveau fichier Python dans le répertoire approprié.

### 2. Chargement dynamique
Les plugins peuvent être rechargés à chaud sans redémarrer l'application (nécessite les droits administrateur).

### 3. Système de métadonnées
Chaque plugin possède des métadonnées (nom, version, auteur, description) accessibles via l'API.

### 4. Validation de configuration
Les plugins peuvent valider leur configuration avant exécution.

### 5. Registre centralisé
Un registre central (`PluginRegistry`) permet d'accéder à tous les types de plugins de manière unifiée.

## Types de plugins

### Actions
Les plugins d'actions permettent d'effectuer des opérations lors de l'exécution des tests.

**Actions disponibles :**
- HTTP Request (GET, POST, PUT, DELETE)
- SSH (exécution de commandes distantes)
- WebDAV (opérations sur serveur WebDAV)
- FTP (transfert de fichiers FTP)
- SFTP (transfert de fichiers sécurisé)

### Rapports
Les plugins de rapports permettent de générer des rapports dans différents formats.

**Rapports disponibles :**
- HTML (exemple fourni)

### Authentification
Les plugins d'authentification permettent d'intégrer différents systèmes d'authentification.

**Méthodes d'authentification disponibles :**
- Local (authentification MongoDB avec JWT)

## Utilisation

### Via l'API

#### Lister tous les plugins
```bash
GET /api/plugins
```

Réponse :
```json
{
  "actions": {
    "http": {
      "mask": [...],
      "class": "HTTPRequestAction",
      "metadata": {...}
    },
    ...
  },
  "reports": {...},
  "auth": {...}
}
```

#### Lister les plugins d'un type
```bash
GET /api/plugins/actions
```

#### Obtenir les informations d'un plugin
```bash
GET /api/plugins/actions/http
```

#### Recharger tous les plugins (admin)
```bash
POST /api/plugins/reload
```

#### Statistiques des plugins
```bash
GET /api/plugins/stats
```

### Via le code Python

```python
from plugins import plugin_registry

# Obtenir tous les plugins
all_plugins = plugin_registry.get_all_plugins()

# Obtenir le gestionnaire d'un type spécifique
action_manager = plugin_registry.get_manager('actions')

# Obtenir une instance de plugin
from plugins.actions import get_action
http_action = get_action('http')

# Exécuter une action
result = http_action.execute({
    'method': 'GET',
    'url': 'https://api.example.com/data'
})

# Recharger les plugins
plugin_registry.reload_all()
```

## Développement de nouveaux plugins

Consultez le [Guide de développement de plugins](PLUGIN_DEVELOPMENT_GUIDE.md) pour créer vos propres plugins.

### Étapes rapides

1. Créez un nouveau fichier Python dans le répertoire approprié
2. Héritez de la classe de base correspondante
3. Implémentez les méthodes abstraites requises
4. Redémarrez l'application ou rechargez les plugins

Exemple minimal :
```python
from plugins.actions.action_base import ActionBase

class MyAction(ActionBase):
    plugin_name = "myaction"
    version = "1.0.0"
    
    def get_metadata(self):
        return {...}
    
    def validate_config(self, config):
        return (True, "")
    
    def get_input_mask(self):
        return [...]
    
    def execute(self, action_context):
        # Votre logique ici
        return self.get_result()
```

## Gestion des dépendances

Si un plugin nécessite des bibliothèques externes, ajoutez-les à `requirements.txt` :

```txt
# Plugin MyAction
requests>=2.28.0
paramiko>=3.0.0
```

## Sécurité

### Isolation
Les plugins s'exécutent dans le même espace que l'application. Assurez-vous que le code des plugins est de confiance.

### Validation
Utilisez toujours `validate_config()` pour valider les entrées utilisateur avant exécution.

### Permissions
Le rechargement des plugins nécessite les droits administrateur.

## Performance

### Chargement
Les plugins sont chargés au démarrage de l'application. Le temps de chargement augmente avec le nombre de plugins.

### Exécution
L'exécution des plugins est synchrone. Pour les opérations longues, envisagez l'utilisation de tâches asynchrones.

### Mise en cache
Le registre des plugins est mis en cache. Utilisez l'API de rechargement pour rafraîchir le cache.

## Débogage

### Logs
Le système de plugins génère des logs lors de la découverte et du chargement :

```
Plugin 'http' chargé avec succès (HTTPRequestAction)
Plugin 'ssh' chargé avec succès (SSHAction)
...
```

### Erreurs courantes

**Plugin non trouvé**
- Vérifiez que le fichier est dans le bon répertoire
- Vérifiez que la classe hérite de la bonne classe de base
- Vérifiez que `plugin_name` est défini

**Erreur de chargement**
- Vérifiez les imports dans votre plugin
- Vérifiez que toutes les méthodes abstraites sont implémentées
- Consultez les logs d'erreur

## Exemples

### Plugin d'action simple
Voir `plugins/actions/http_request_action.py`

### Plugin de rapport
Voir `plugins/reports/html_report_plugin.py`

### Plugin d'authentification
Voir `plugins/auth/local_auth_plugin.py`

## Roadmap

- [ ] Support des plugins asynchrones
- [ ] Système de permissions par plugin
- [ ] Interface graphique pour gérer les plugins
- [ ] Marketplace de plugins
- [ ] Tests automatisés pour les plugins
- [ ] Versioning et migration de plugins
- [ ] Sandbox d'exécution pour les plugins

## Contribution

Pour contribuer au système de plugins :

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Développez votre plugin
4. Testez votre plugin
5. Soumettez une pull request

## Support

Pour toute question :
- Consultez la documentation
- Ouvrez une issue sur GitHub
- Contactez l'équipe de développement

## Licence

Le système de plugins fait partie de TestGyver et est distribué sous la même licence.
