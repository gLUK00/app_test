# Guide de développement de plugins pour TestGyver

## Vue d'ensemble

TestGyver utilise un système de plugins modulaire et extensible qui permet d'ajouter dynamiquement de nouvelles fonctionnalités sans modifier le code principal de l'application. Ce guide explique comment créer vos propres plugins.

## Types de plugins disponibles

### 1. Plugins d'actions (`plugins/actions/`)
Les plugins d'actions permettent d'effectuer différentes opérations lors de l'exécution des tests (requêtes HTTP, commandes SSH, opérations FTP, etc.).

### 2. Plugins de rapports (`plugins/reports/`)
Les plugins de rapports permettent de générer des rapports dans différents formats (PDF, HTML, Excel, JSON, etc.).

### 3. Plugins d'authentification (`plugins/auth/`)
Les plugins d'authentification permettent d'intégrer différents systèmes d'authentification (LDAP, OAuth, SAML, etc.).

## Architecture du système de plugins

### Gestionnaire de plugins (`PluginManager`)

Le `PluginManager` est le composant central qui :
- Découvre automatiquement les plugins dans un répertoire
- Charge dynamiquement les classes de plugins
- Gère l'enregistrement et le désenregistrement des plugins
- Fournit des informations sur les plugins disponibles

### Classes de base

Chaque type de plugin hérite d'une classe de base spécifique :
- `ActionBase` pour les actions
- `ReportBase` pour les rapports
- `AuthBase` pour l'authentification

Toutes ces classes héritent de `PluginBase`.

## Créer un plugin d'action

### Étape 1 : Créer le fichier du plugin

Créez un nouveau fichier Python dans `plugins/actions/`, par exemple `custom_action.py`.

### Étape 2 : Implémenter la classe

```python
"""Plugin d'action personnalisée."""
from plugins.actions.action_base import ActionBase


class CustomAction(ActionBase):
    """Description de votre action personnalisée."""
    
    # Métadonnées du plugin
    plugin_name = "custom"  # Nom unique (obligatoire)
    version = "1.0.0"
    author = "Votre nom"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Description détaillée de votre action"
        }
    
    def validate_config(self, config):
        """
        Valide la configuration de l'action.
        
        Args:
            config (dict): Configuration à valider
        
        Returns:
            tuple: (bool, str) - (succès, message d'erreur éventuel)
        """
        # Validez les champs requis
        if 'required_field' not in config:
            return (False, "Le champ 'required_field' est obligatoire")
        return (True, "")
    
    def get_input_mask(self):
        """
        Retourne le masque de saisie pour les paramètres.
        
        Returns:
            list: Liste de dictionnaires définissant les champs du formulaire
        """
        return [
            {
                "name": "param1",
                "type": "string",  # string, number, boolean, textarea, select, checkbox
                "label": "Paramètre 1",
                "placeholder": "Valeur du paramètre",
                "required": True
            },
            {
                "name": "param2",
                "type": "select",
                "label": "Paramètre 2",
                "options": ["option1", "option2", "option3"],
                "required": False
            }
        ]
    
    def get_output_variables(self):
        """
        Retourne la liste des variables de sortie possibles pour cette action.
        Ces variables pourront être utilisées dans les actions suivantes du même test.
        
        Returns:
            list: Liste de dictionnaires définissant les variables de sortie
        """
        return [
            {
                "name": "custom_result",
                "description": "Résultat de l'opération personnalisée",
                "type": "string"  # string, number, boolean
            },
            {
                "name": "custom_count",
                "description": "Nombre d'éléments traités",
                "type": "number"
            }
        ]
    
    def execute(self, action_context):
        """
        Exécute l'action avec le contexte fourni.
        
        Args:
            action_context (dict): Paramètres de l'action
        
        Returns:
            dict: Résultat de l'exécution
        """
        try:
            # Récupérer les paramètres
            param1 = action_context.get('param1')
            param2 = action_context.get('param2')
            
            self.add_trace(f"Exécution avec param1={param1}, param2={param2}")
            
            # Effectuer votre traitement
            result_value = "Résultat de l'opération"
            count = 42
            
            # Préparer les variables de sortie avec leurs valeurs réelles
            output_vars = {
                "custom_result": result_value,
                "custom_count": count
            }
            
            # En cas de succès
            self.set_code(0)
            self.add_trace("Action exécutée avec succès")
            
            # Passer les variables de sortie à get_result()
            return self.get_result({
                "custom_data": "Données de résultat"
            }, output_vars)
            
        except Exception as e:
            self.set_code(1)
            self.add_trace(f"Erreur : {str(e)}")
            return self.get_result()
```

### Étape 3 : Tester votre plugin

Le plugin sera automatiquement découvert et chargé au démarrage de l'application. Vous pouvez le tester via :

1. L'API : `GET /api/plugins/actions/custom`
2. L'interface web lors de l'ajout d'une action à un test

### Étape 4 : Recharger les plugins (développement)

Pour recharger les plugins sans redémarrer l'application (nécessite les droits admin) :

```bash
POST /api/plugins/actions/reload
```

## Variables de sortie des actions

Les variables de sortie permettent aux actions de partager des données entre elles lors de l'exécution d'un test. Cette fonctionnalité est essentielle pour créer des scénarios de tests complexes où les actions dépendent les unes des autres.

### Définir les variables de sortie disponibles

La méthode `get_output_variables()` définit la liste des variables que votre action peut produire :

```python
def get_output_variables(self):
    """Retourne la liste des variables de sortie possibles."""
    return [
        {
            "name": "nom_unique_de_la_variable",
            "description": "Description claire de ce que contient la variable",
            "type": "string"  # string, number ou boolean
        }
    ]
```

**Important :** 
- Préfixez le nom des variables par un identifiant unique à votre action (ex: `http_`, `ssh_`, `custom_`)
- Les noms doivent être en snake_case
- Fournissez des descriptions claires pour aider les utilisateurs

### Retourner les valeurs des variables

Dans la méthode `execute()`, créez un dictionnaire avec les valeurs réelles des variables et passez-le à `get_result()` :

```python
def execute(self, action_context):
    try:
        # Votre logique métier
        status = 200
        response = "Success"
        
        # Préparer les variables de sortie
        output_vars = {
            "custom_status": status,
            "custom_response": response
        }
        
        self.set_code(0)
        return self.get_result(result_data, output_vars)
    except Exception as e:
        self.set_code(1)
        # Même en cas d'erreur, vous pouvez retourner des variables
        output_vars = {
            "custom_status": 500,
            "custom_response": str(e)
        }
        return self.get_result(None, output_vars)
```

### Utilisation par l'utilisateur

Lors de la configuration d'une action dans l'interface utilisateur :

1. L'utilisateur voit la liste des variables de sortie disponibles
2. Il peut choisir de mapper chaque variable vers une variable du test
3. Les variables mappées deviennent accessibles aux actions suivantes

### Exemple complet

```python
class DatabaseQueryAction(ActionBase):
    plugin_name = "db_query"
    
    def get_output_variables(self):
        return [
            {
                "name": "db_row_count",
                "description": "Nombre de lignes retournées par la requête",
                "type": "number"
            },
            {
                "name": "db_first_result",
                "description": "Premier résultat de la requête (JSON)",
                "type": "string"
            },
            {
                "name": "db_query_time",
                "description": "Temps d'exécution de la requête en ms",
                "type": "number"
            }
        ]
    
    def execute(self, action_context):
        import time
        import json
        
        start = time.time()
        query = action_context.get('query')
        
        # Exécution de la requête (exemple simplifié)
        results = execute_db_query(query)
        query_time = (time.time() - start) * 1000
        
        # Préparer les variables de sortie
        output_vars = {
            "db_row_count": len(results),
            "db_first_result": json.dumps(results[0]) if results else "",
            "db_query_time": query_time
        }
        
        self.set_code(0)
        return self.get_result({
            "rows": len(results),
            "data": results[:10]  # Limiter pour l'affichage
        }, output_vars)
```

Pour plus d'informations sur l'utilisation des variables de sortie côté utilisateur, consultez [OUTPUT_VARIABLES.md](OUTPUT_VARIABLES.md).

## Fonctions JavaScript dans les plugins d'actions

Les plugins d'actions peuvent définir des fonctions JavaScript personnalisées qui s'exécutent côté client pour améliorer l'expérience utilisateur lors de la configuration des actions. Ces fonctions permettent d'ajouter une validation côté client, des interactions dynamiques, ou des modifications de l'interface en temps réel.

### Fonctions JavaScript disponibles

#### 1. `jsShowForm` - Personnalisation de l'affichage du formulaire

Cette fonction est appelée après la génération des champs dynamiques du formulaire de configuration de l'action. Elle permet de :
- Modifier l'apparence des champs
- Ajouter des écouteurs d'événements
- Afficher des informations contextuelles
- Valider en temps réel les valeurs saisies

**Signature :**
```python
def get_js_show_form(self):
    """
    Retourne le code JavaScript à exécuter lors de l'affichage du formulaire.
    
    IMPORTANT: Retourner uniquement le CORPS de la fonction, pas la déclaration.
    Le framework crée automatiquement new Function('actionConfig', code).
    
    Returns:
        str: Code JavaScript (corps uniquement) ou None
    """
    return """
// actionConfig: objet contenant les valeurs actuelles des champs
// Votre code JavaScript ici

// Exemple : ajouter un écouteur sur un champ
const myField = document.getElementById('my_field');
if (myField) {
    myField.addEventListener('change', function() {
        console.log('Valeur changée:', this.value);
    });
}
"""
```

**Paramètres :**
- `actionConfig` : Objet JavaScript contenant les valeurs actuelles des champs de configuration (utilisé lors de l'édition d'une action existante)

**Valeur de retour :** Aucune

#### 2. `jsValidateForm` - Validation personnalisée du formulaire

Cette fonction est appelée lors de la validation du formulaire, avant la soumission. Elle permet de :
- Valider des règles métier complexes
- Vérifier la cohérence entre plusieurs champs
- Valider l'existence de ressources (variables, fichiers, etc.)
- Afficher des messages d'erreur personnalisés

**Signature :**
```python
def get_js_validate_form(self):
    """
    Retourne le code JavaScript à exécuter lors de la validation du formulaire.
    
    Returns:
        str: Code JavaScript de la fonction jsValidateForm ou None
    """
    return """
function jsValidateForm(actionConfig, variables) {
    // actionConfig: objet contenant les valeurs actuelles des champs
    // variables: tableau des variables du test en cours
    
    // Votre validation ici
    if (!actionConfig.my_field) {
        return {
            isValid: false,
            errorMessage: 'Le champ my_field est obligatoire'
        };
    }
    
    // Validation réussie
    return {
        isValid: true,
        errorMessage: ''
    };
}
"""
```

**Paramètres :**
- `actionConfig` : Objet JavaScript contenant les valeurs actuelles de tous les champs du formulaire
- `variables` : Tableau des noms des variables définies dans le test en cours

**Valeur de retour :** Objet avec deux propriétés :
- `isValid` (boolean) : `true` si la validation est réussie, `false` sinon
- `errorMessage` (string) : Message d'erreur à afficher si `isValid` est `false` (vide si réussite)

### Exemple complet : Plugin VarAction

Voici un exemple réel du plugin VarAction qui utilise les deux fonctions JavaScript :

```python
class VarAction(ActionBase):
    plugin_name = "var"
    label = "Variables (Conversion)"
    
    def get_js_show_form(self):
        """
        Met en évidence la variable sélectionnée si elle n'existe pas.
        IMPORTANT: Retourner uniquement le corps, pas 'function jsShowForm(...)'
        """
        return """
const variableSelect = document.getElementById('variable_name');
if (!variableSelect) return;

// Ajouter un écouteur pour mettre à jour le style
variableSelect.addEventListener('change', function() {
    const selectedValue = this.value;
    if (!selectedValue) {
        this.classList.remove('is-valid', 'is-invalid');
        return;
    }
    
    const variables = window.testActionsManager ? 
        window.testActionsManager.variables : [];
    
    if (variables.includes(selectedValue)) {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
    } else {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
    }
});

// Déclencher la validation initiale
if (actionConfig && actionConfig.variable_name) {
    variableSelect.value = actionConfig.variable_name;
    variableSelect.dispatchEvent(new Event('change'));
}
"""
    
    def get_js_validate_form(self):
        """
        Valide que la variable sélectionnée existe dans les variables du test.
        IMPORTANT: Retourner uniquement le corps, pas 'function jsValidateForm(...)'
        """
        return """
const variableName = actionConfig.variable_name;

if (!variableName || variableName.trim() === '') {
    return {
        isValid: false,
        errorMessage: 'Veuillez sélectionner une variable à convertir'
    };
}

if (!variables || !Array.isArray(variables)) {
    return {isValid: true, errorMessage: ''};
}

if (!variables.includes(variableName)) {
    return {
        isValid: false,
        errorMessage: `La variable "${variableName}" n'existe pas dans les variables du test. Veuillez créer cette variable avant de l'utiliser.`
    };
}

return {isValid: true, errorMessage: ''};
"""
```

### Bonnes pratiques

1. **Retourner `None` si non utilisé** : Si vous n'avez pas besoin de fonctions JavaScript, retournez simplement `None` (comportement par défaut de `ActionBase`)

2. **Gestion des erreurs** : Ajoutez toujours des vérifications pour éviter les erreurs JavaScript
   ```javascript
   const myField = document.getElementById('my_field');
   if (!myField) {
       console.warn('Champ my_field non trouvé');
       return;
   }
   ```

3. **Utiliser les classes Bootstrap** : Pour la cohérence visuelle, utilisez les classes Bootstrap existantes (`is-valid`, `is-invalid`, etc.)

4. **Console.log pour le débogage** : Utilisez `console.log()` pour faciliter le débogage
   ```javascript
   console.log('MonAction: jsValidateForm appelée', actionConfig);
   ```

5. **Accéder au gestionnaire d'actions** : Vous pouvez accéder à `window.testActionsManager` pour récupérer les variables du test et d'autres informations

6. **Ne pas bloquer l'interface** : Évitez les traitements longs dans `jsShowForm`. Pour `jsValidateForm`, les validations doivent être rapides

7. **Messages d'erreur clairs** : Fournissez des messages d'erreur explicites pour aider l'utilisateur

### Considérations de sécurité

- Le code JavaScript est exécuté côté client avec les privilèges de l'utilisateur
- Évitez de manipuler des données sensibles dans le code JavaScript
- Les validations JavaScript ne remplacent pas les validations côté serveur (méthode `validate_config()`)

### Extension future

Le mécanisme des fonctions JavaScript est extensible. D'autres fonctions pourront être ajoutées à l'avenir selon les besoins, par exemple :
- `jsOnFieldChange` : Appelée lors du changement d'un champ spécifique
- `jsBeforeSubmit` : Appelée juste avant la soumission du formulaire
- `jsAfterSave` : Appelée après la sauvegarde réussie de l'action

## Créer un plugin de rapport
```

## Créer un plugin de rapport

### Structure de base

```python
"""Plugin de rapport personnalisé."""
from plugins.reports.report_base import ReportBase


class CustomReport(ReportBase):
    """Description de votre rapport personnalisé."""
    
    # Métadonnées du plugin
    plugin_name = "custom_report"
    version = "1.0.0"
    author = "Votre nom"
    
    def get_metadata(self):
        """Retourne les métadonnées du rapport."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Description de votre rapport",
            "output_format": self.get_output_format()
        }
    
    def validate_config(self, config):
        """Valide la configuration du rapport."""
        return (True, "")
    
    def get_output_format(self):
        """Retourne le format de sortie."""
        return "custom"  # pdf, html, excel, json, xml, etc.
    
    def get_configuration_schema(self):
        """Retourne le schéma de configuration."""
        return [
            {
                "name": "title",
                "type": "string",
                "label": "Titre du rapport",
                "required": True
            }
        ]
    
    def generate(self, test_results, config=None):
        """
        Génère le rapport.
        
        Args:
            test_results (dict): Résultats des tests
            config (dict): Configuration personnalisée
        
        Returns:
            dict: Résultat de la génération
        """
        try:
            # Générer le rapport
            # ...
            
            return {
                "success": True,
                "message": "Rapport généré avec succès",
                "file_path": "/path/to/report.ext",
                "data": "Contenu du rapport si applicable"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur : {str(e)}",
                "file_path": None,
                "data": None
            }
```

## Créer un plugin d'authentification

### Structure de base

```python
"""Plugin d'authentification personnalisé."""
from plugins.auth.auth_base import AuthBase


class CustomAuth(AuthBase):
    """Description de votre système d'authentification."""
    
    # Métadonnées du plugin
    plugin_name = "custom_auth"
    version = "1.0.0"
    author = "Votre nom"
    
    def get_metadata(self):
        """Retourne les métadonnées."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Description de votre système d'authentification",
            "auth_type": self.get_auth_type()
        }
    
    def validate_config(self, config):
        """Valide la configuration."""
        return (True, "")
    
    def get_auth_type(self):
        """Retourne le type d'authentification."""
        return "custom"
    
    def get_configuration_schema(self):
        """Retourne le schéma de configuration."""
        return []
    
    def authenticate(self, credentials):
        """Authentifie un utilisateur."""
        try:
            username = credentials.get('username')
            password = credentials.get('password')
            
            # Effectuer l'authentification
            # ...
            
            return {
                "success": True,
                "message": "Authentification réussie",
                "user": {
                    "id": "user_id",
                    "name": "User Name",
                    "email": "user@example.com",
                    "roles": ["user"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erreur : {str(e)}",
                "user": None
            }
    
    def validate_token(self, token):
        """Valide un token."""
        # Implémenter la validation
        return {
            "valid": True,
            "user": {}
        }
    
    def logout(self, user_id):
        """Déconnecte un utilisateur."""
        return True
    
    def supports_registration(self):
        """Indique si l'enregistrement est supporté."""
        return False
    
    def supports_password_reset(self):
        """Indique si la réinitialisation de mot de passe est supportée."""
        return False
```

## API de gestion des plugins

### Lister tous les plugins
```
GET /api/plugins
```

### Lister les plugins d'un type
```
GET /api/plugins/{type}
```

### Obtenir les informations d'un plugin
```
GET /api/plugins/{type}/{name}
```

### Recharger tous les plugins (admin)
```
POST /api/plugins/reload
```

### Recharger les plugins d'un type (admin)
```
POST /api/plugins/{type}/reload
```

## Bonnes pratiques

1. **Nommage** : Utilisez des noms de fichiers descriptifs et en snake_case
2. **Documentation** : Documentez votre code avec des docstrings
3. **Validation** : Implémentez toujours `validate_config()` pour valider les paramètres
4. **Gestion d'erreurs** : Gérez les exceptions et retournez des messages d'erreur clairs
5. **Métadonnées** : Remplissez toutes les métadonnées du plugin
6. **Tests** : Testez votre plugin avant de le déployer en production
7. **Versioning** : Utilisez le versioning sémantique (MAJOR.MINOR.PATCH)

## Dépendances

Si votre plugin nécessite des dépendances externes, ajoutez-les à `requirements.txt` :

```
# Mon plugin personnalisé
ma-librairie==1.2.3
```

## Distribution

Pour partager votre plugin :

1. Copiez le fichier du plugin dans le répertoire approprié
2. Redémarrez l'application ou utilisez l'API de rechargement
3. Le plugin sera automatiquement découvert et chargé

## Débogage

Pour activer les logs de débogage des plugins, utilisez :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Les logs incluront les informations sur :
- La découverte des plugins
- Le chargement des classes
- Les erreurs éventuelles

## Support

Pour toute question ou problème, consultez la documentation ou contactez l'équipe de développement.
