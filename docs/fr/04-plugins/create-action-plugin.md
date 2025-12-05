# Créer un Nouveau Plugin d'Action

Ce guide détaille le processus de création d'un nouveau plugin d'action pour TestGyver. Les plugins d'action vous permettent d'étendre les capacités de l'application en ajoutant de nouveaux types de tâches automatisées (ex: interaction base de données, appels API, manipulation de fichiers).

## Prérequis

*   Connaissance de base de Python.
*   Accès au répertoire `plugins/actions/` du projet.

## Guide Pas à Pas

### 1. Créer le Fichier du Plugin

Créez un nouveau fichier Python dans le répertoire `plugins/actions/`. Le nom du fichier doit être descriptif (ex: `mon_action_perso.py`).

### 2. Hériter de `ActionBase`

Votre classe doit hériter de `ActionBase` et implémenter les méthodes requises.

```python
from plugins.actions.action_base import ActionBase

class MonActionPerso(ActionBase):
    """Description de ce que fait votre action."""
    
    # Métadonnées
    plugin_name = "mon_action_perso"  # Nom interne unique
    label = "Mon Action Perso"        # Nom affiché dans l'UI
    version = "1.0.0"
    author = "Votre Nom"
```

### 3. Implémenter les Méthodes Requises

Vous devez implémenter les méthodes suivantes :

#### `get_metadata(self)`

Retourne les informations de base sur le plugin.

```python
    def get_metadata(self):
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Description détaillée de l'action."
        }
    
#### `validate_config(self, config)`

Valide les paramètres fournis par l'utilisateur avant l'exécution.

```python
    def validate_config(self, config):
        if 'target_host' not in config:
            return (False, "L'hôte cible est requis")
        return (True, "")
```

#### `get_input_mask(self)`

Définit le formulaire UI pour configurer l'action. Types supportés : `string`, `number`, `boolean`, `textarea`, `select`, `checkbox`, `select-var-test`.

```python
    def get_input_mask(self):
        return [
            {
                "name": "target_host",
                "type": "string",
                "label": "Hôte Cible",
                "placeholder": "192.168.1.1",
                "required": True
            },
            {
                "name": "port",
                "type": "number",
                "label": "Port",
                "placeholder": 8080,
                "required": False
            }
        ]
```

#### `get_output_variables(self)`

Définit les variables que cette action va produire, qui peuvent être utilisées par les actions suivantes.

```python
    def get_output_variables(self):
        return [
            {
                "name": "execution_result",
                "description": "Résultat de l'opération",
                "type": "string"
            }
        ]
```

#### `execute(self, context)`

La logique centrale de votre action. L'objet `context` fournit l'accès aux variables et aux données d'environnement.

```python
    def execute(self, context):
        # Accéder aux paramètres d'entrée
        host = context.get('target_host')
        
        # Effectuer votre logique ici
        try:
            # ... faire quelque chose ...
            result = "Succès"
            
            # Définir les variables de sortie
            self.output_variables['execution_result'] = result
            
            return (0, ["Connecté à " + host, "Opération réussie"])
        except Exception as e:
            return (1, [f"Erreur : {str(e)}"])
```

### 4. Enregistrement

Le `PluginManager` découvre automatiquement les plugins dans le répertoire `plugins/actions/`. Aucun enregistrement manuel n'est requis. Redémarrez simplement l'application.

## Bonnes Pratiques

*   **Gestion d'Erreur** : Enveloppez toujours votre logique d'exécution dans des blocs try/except pour éviter de faire planter le lanceur de tests.
*   **Logging** : Retournez des traces détaillées (deuxième élément du tuple de retour) pour aider les utilisateurs à déboguer les problèmes.
*   **Validation** : Soyez strict dans `validate_config` pour attraper les erreurs tôt.
