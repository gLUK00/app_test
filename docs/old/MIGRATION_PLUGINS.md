# Migration vers le nouveau système de plugins

## Vue d'ensemble

Ce document explique comment migrer depuis l'ancien système de plugins vers le nouveau système modulaire.

## Changements principaux

### Avant (ancien système)

```python
# plugins/actions/__init__.py
from .http_request_action import HTTPRequestAction
from .ssh_action import SSHAction

ACTION_REGISTRY = {
    'http': HTTPRequestAction,
    'ssh': SSHAction
}

# Pour ajouter une nouvelle action, il fallait :
# 1. Créer le fichier de l'action
# 2. L'importer dans __init__.py
# 3. L'ajouter manuellement au ACTION_REGISTRY
```

### Après (nouveau système)

```python
# plugins/actions/__init__.py
from plugins.plugin_manager import PluginManager

# Le gestionnaire découvre automatiquement tous les plugins
action_manager = PluginManager('actions', ActionBase)
action_manager.discover_plugins()

# Pour ajouter une nouvelle action, il suffit de :
# 1. Créer le fichier de l'action dans plugins/actions/
# 2. Hériter de ActionBase
# 3. Définir plugin_name
# C'est tout ! Le plugin sera automatiquement découvert et chargé
```

## Migration du code existant

### Actions existantes

Toutes les actions existantes ont été mises à jour pour inclure :

```python
class HTTPRequestAction(ActionBase):
    # Nouvelles métadonnées requises
    plugin_name = "http"
    version = "1.0.0"
    author = "TestGyver Team"
    
    # Nouvelles méthodes requises
    def get_metadata(self):
        return {...}
    
    def validate_config(self, config):
        return (True, "")
```

### Utilisation dans le code

L'API reste **rétrocompatible** :

```python
# Ancien code (toujours fonctionnel)
from plugins.actions import get_action, get_all_actions

action = get_action('http')
all_actions = get_all_actions()

# Nouveau code (recommandé)
from plugins.actions import action_manager

action = action_manager.get_plugin('http')
all_plugins = action_manager.list_plugins()
```

## Nouveaux types de plugins

### Plugins de rapports

```python
from plugins.reports import get_report

# Obtenir un plugin de rapport
html_report = get_report('html')

# Générer un rapport
result = html_report.generate(test_results, config)
```

### Plugins d'authentification

```python
from plugins.auth import get_auth

# Obtenir un plugin d'authentification
local_auth = get_auth('local')

# Authentifier un utilisateur
result = local_auth.authenticate({
    'email': 'user@example.com',
    'password': 'password'
})
```

## Nouvelles API REST

### Lister tous les plugins
```bash
GET /api/plugins
```

### Obtenir un plugin spécifique
```bash
GET /api/plugins/actions/http
```

### Recharger les plugins (admin)
```bash
POST /api/plugins/reload
```

## Checklist de migration

Pour migrer votre code :

- [ ] Vérifier que toutes les actions ont `plugin_name` défini
- [ ] Vérifier que les méthodes `get_metadata()` et `validate_config()` sont implémentées
- [ ] Tester le chargement automatique des plugins
- [ ] Mettre à jour les imports si nécessaire
- [ ] Tester les nouvelles API REST
- [ ] Lire la documentation des nouveaux types de plugins

## Avantages du nouveau système

1. **Pas de modification du code principal** : Ajoutez un plugin simplement en créant un fichier
2. **Rechargement à chaud** : Rechargez les plugins sans redémarrer l'application
3. **Extensibilité** : Ajoutez facilement de nouveaux types de plugins
4. **Métadonnées** : Chaque plugin expose ses informations via l'API
5. **Validation** : Validation intégrée de la configuration
6. **API unifiée** : Même interface pour tous les types de plugins

## Compatibilité

### Compatibilité ascendante

Le nouveau système est **100% compatible** avec l'ancien code :
- `ACTION_REGISTRY` existe toujours
- `get_action()` et `get_all_actions()` fonctionnent toujours
- Les actions existantes continuent de fonctionner sans modification

### Dépréciation

Aucune fonctionnalité n'est dépréciée. L'ancienne API restera disponible.

## Support

En cas de problème lors de la migration :

1. Consultez les logs de l'application
2. Vérifiez que les plugins sont dans les bons répertoires
3. Vérifiez que les classes héritent des bonnes classes de base
4. Consultez `PLUGIN_DEVELOPMENT_GUIDE.md`

## Exemple complet de migration

### Avant

```python
# mon_action.py
from plugins.actions.action_base import ActionBase

class MonAction(ActionBase):
    def get_input_mask(self):
        return [...]
    
    def execute(self, action_context):
        # ...
        return self.get_result()

# __init__.py (modification nécessaire)
from .mon_action import MonAction
ACTION_REGISTRY['mon_action'] = MonAction
```

### Après

```python
# mon_action.py (fichier créé dans plugins/actions/)
from plugins.actions.action_base import ActionBase

class MonAction(ActionBase):
    plugin_name = "mon_action"  # Ajouté
    version = "1.0.0"           # Ajouté
    author = "Mon nom"          # Ajouté
    
    def get_metadata(self):     # Ajouté
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Mon action personnalisée"
        }
    
    def validate_config(self, config):  # Ajouté
        return (True, "")
    
    def get_input_mask(self):
        return [...]
    
    def execute(self, action_context):
        # ...
        return self.get_result()

# __init__.py (aucune modification nécessaire !)
# Le plugin est découvert automatiquement
```

## Conclusion

Le nouveau système de plugins offre une architecture plus modulaire et extensible tout en maintenant une compatibilité totale avec l'ancien code. La migration est simple et ne nécessite que l'ajout de quelques métadonnées aux plugins existants.
