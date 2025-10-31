# Système de Diagnostic des Erreurs de Plugins

## Vue d'ensemble

Le système de diagnostic des erreurs de plugins permet de détecter, enregistrer et visualiser toutes les erreurs qui surviennent lors du chargement ou de l'exécution des plugins dans TestGyver.

## Fonctionnalités

### 1. Capture automatique des erreurs

Toutes les erreurs sont automatiquement capturées lors de :
- **Chargement des plugins** : erreurs de syntaxe, imports manquants, etc.
- **Exécution des actions** : erreurs d'exécution, exceptions non gérées

### 2. Informations enregistrées

Pour chaque erreur, les informations suivantes sont enregistrées :
- Nom du plugin
- Type de plugin (actions, reports, auth)
- Message d'erreur
- Traceback complet
- Timestamp de l'erreur

### 3. Consultation des erreurs

#### Via l'interface web

**Page d'administration : `/admin/plugins/errors`**

Accessible uniquement aux administrateurs, cette page affiche :
- Statistiques globales (plugins chargés, erreurs, types)
- Filtrage par type de plugin
- Liste détaillée des erreurs avec :
  - Message d'erreur
  - Trace complète (pliable)
  - Horodatage

#### Via l'API REST

**Endpoint : `GET /api/plugins/errors`**

Paramètres optionnels :
- `plugin_type` : Filtrer par type de plugin

Réponse :
```json
{
  "success": true,
  "count": 1,
  "errors": [
    {
      "plugin_name": "webdav_action",
      "plugin_type": "actions",
      "error": "No module named 'webdav4'",
      "traceback": "Traceback (most recent call last):\n...",
      "timestamp": "2025-10-31T11:16:13.389339"
    }
  ]
}
```

## Utilisation

### Pour les développeurs de plugins

Aucune action requise - les erreurs sont automatiquement capturées !

### Pour les administrateurs

1. **Accéder à la page de diagnostic** :
   - Menu Administration → "Erreurs de plugins"

2. **Identifier les problèmes** :
   - Consultez la liste des erreurs
   - Cliquez sur "Voir la trace complète" pour les détails

3. **Résoudre les erreurs** :
   - Installez les dépendances manquantes
   - Corrigez les erreurs de syntaxe
   - Vérifiez les imports

4. **Rafraîchir** :
   - Cliquez sur "Rafraîchir" pour recharger les plugins
   - Les erreurs corrigées disparaîtront automatiquement

## API PluginManager

### Méthodes disponibles

```python
# Récupérer les erreurs
errors = plugin_manager.get_errors()

# Vérifier s'il y a des erreurs
has_errors = plugin_manager.has_errors()

# Effacer les erreurs
plugin_manager.clear_errors()

# Recharger les plugins (efface aussi les erreurs)
plugin_manager.reload_plugins()
```

### Exemple d'utilisation

```python
from plugins.plugin_manager import PluginManager
from plugins.actions.action_base import ActionBase

# Créer le gestionnaire
manager = PluginManager('actions', ActionBase)

# Charger les plugins
manager.discover_plugins()

# Vérifier les erreurs
if manager.has_errors():
    for error in manager.get_errors():
        print(f"Erreur dans {error['plugin_name']}: {error['error']}")
```

## Améliorations du CampainExecutor

Les erreurs d'exécution des actions incluent maintenant :
- Le message d'erreur
- Le traceback complet
- L'horodatage de l'erreur

Ces informations sont ajoutées aux logs du rapport et visibles dans l'interface de suivi en temps réel.

## Tests

Un script de test est disponible : `_build/test_plugin_errors.py`

```bash
python3 _build/test_plugin_errors.py
```

Ce script affiche :
- Le nombre de plugins chargés
- Le nombre d'erreurs détectées
- Les détails de chaque erreur

## Cas d'usage typiques

### 1. Module manquant

**Erreur** : `ModuleNotFoundError: No module named 'webdav4'`

**Solution** :
```bash
pip install webdav4
```

### 2. Erreur de syntaxe

**Erreur** : `SyntaxError: f-string expression part cannot include a backslash`

**Solution** : Corriger la syntaxe dans le fichier du plugin

### 3. Import invalide

**Erreur** : `ImportError: cannot import name 'InvalidClass'`

**Solution** : Vérifier les imports dans le plugin

## Bonnes pratiques

1. **Vérifier régulièrement** la page d'erreurs des plugins
2. **Installer toutes les dépendances** listées dans requirements.txt
3. **Tester les plugins** après modification avec le script de test
4. **Consulter les logs** pour les erreurs d'exécution
5. **Documenter les dépendances** de vos plugins

## Dépannage

### Les erreurs ne s'affichent pas

1. Vérifiez que vous êtes connecté en tant qu'administrateur
2. Actualisez la page
3. Vérifiez les logs de la console navigateur

### Les plugins ne se rechargent pas

1. Redémarrez l'application Flask
2. Vérifiez que le venv est activé
3. Installez les dépendances manquantes

### Erreur lors de l'exécution

1. Consultez les logs du rapport d'exécution
2. La trace complète est incluse dans les logs
3. Corrigez le code du plugin et relancez

## Support

Pour signaler un bug ou demander de l'aide :
- Consultez les logs de l'application
- Utilisez la page de diagnostic des plugins
- Vérifiez la documentation du plugin concerné
