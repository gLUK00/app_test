# Plugin VarAction - Conversion de Variables

## Description

Le plugin **VarAction** permet de convertir les variables d'un test en différents types de données. Cela est particulièrement utile pour :
- Convertir des réponses HTTP (strings) en types typés (int, float, bool)
- Préparer des données pour des assertions ou des calculs
- Transformer des données JSON en structures Python
- Normaliser les types de données entre différentes actions

## Métadonnées

- **Nom du plugin** : `var`
- **Label** : Variables (Conversion)
- **Version** : 1.0.0
- **Auteur** : TestGyver Team

## Variables d'entrée

### 1. variable_name (obligatoire)
- **Type** : `select-var-test` (nouveau type de champ)
- **Description** : Nom de la variable du test à convertir
- **Format** : Sélection parmi les variables existantes du test en cours
- **Exemple** : `my_response_code`, `user_id`, `price`

### 2. target_type (obligatoire)
- **Type** : `select`
- **Description** : Type de données cible pour la conversion
- **Options disponibles** :
  - `int` : Entier (nombre sans décimales)
  - `float` : Décimal (nombre avec décimales)
  - `bool` : Booléen (True/False)
  - `list` : Liste (tableau)
  - `dict` : Dictionnaire (objet JSON)
  - `json` : String JSON formatée

## Variables de sortie

### converted_value
- **Type** : Mixed (dépend du type cible)
- **Description** : Valeur convertie de la variable
- **Utilisation** : Peut être mappée à une variable du test pour utilisation dans les actions suivantes

## Types de conversion supportés

### Conversion vers `int`
Convertit une valeur en entier.

**Exemples** :
```
"42" → 42
3.14 → 3
"123" → 123
```

**Cas d'erreur** : Valeurs non numériques comme `"abc"`

### Conversion vers `float`
Convertit une valeur en nombre décimal.

**Exemples** :
```
"3.14" → 3.14
42 → 42.0
"2.5" → 2.5
```

**Cas d'erreur** : Valeurs non numériques comme `"abc"`

### Conversion vers `bool`
Convertit une valeur en booléen avec gestion intelligente des strings.

**Exemples** :
```
"true" → True
"false" → False
"1" → True
"0" → False
"yes" → True
"no" → False
"oui" → True
1 → True
0 → False
```

### Conversion vers `list`
Convertit une valeur en liste.

**Exemples** :
```
"[1, 2, 3]" → [1, 2, 3]  (parsing JSON)
"hello" → ["hello"]  (encapsulation)
(1, 2, 3) → [1, 2, 3]  (conversion de tuple)
'{"a": 1}' → [{"a": 1}]  (objet JSON dans liste)
```

### Conversion vers `dict`
Convertit une string JSON en dictionnaire.

**Exemples** :
```
'{"key": "value"}' → {"key": "value"}
'{"id": 42, "name": "test"}' → {"id": 42, "name": "test"}
{"existing": "dict"} → {"existing": "dict"}  (inchangé)
```

**Cas d'erreur** : 
- String qui n'est pas du JSON valide
- JSON qui n'est pas un objet (ex: `"[1,2,3]"`)

### Conversion vers `json`
Convertit une valeur en string JSON formatée.

**Exemples** :
```
{"key": "value"} → '{\n  "key": "value"\n}'
[1, 2, 3] → '[\n  1,\n  2,\n  3\n]'
'{"already": "json"}' → '{"already": "json"}'  (validation)
```

## Nouveau type de champ : `select-var-test`

Le plugin VarAction introduit un nouveau type de champ pour les masques de saisie : **`select-var-test`**.

### Caractéristiques
- **Type** : Liste déroulante (select)
- **Source de données** : Variables du test en cours
- **Mise à jour** : Dynamique en fonction des variables définies
- **Utilisation** : Permet de sélectionner une variable existante du test

### Implémentation JavaScript

Le fichier `static/test_actions.js` a été étendu pour supporter ce nouveau type :

```javascript
} else if (field.type === 'select-var-test') {
    // Nouveau type : sélection parmi les variables du test
    input = document.createElement('select');
    input.className = 'form-select';
    
    // Option par défaut
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '-- Sélectionner une variable --';
    input.appendChild(defaultOption);
    
    // Ajouter les variables du test
    this.variables.forEach(variable => {
        const opt = document.createElement('option');
        opt.value = variable;
        opt.textContent = variable;
        input.appendChild(opt);
    });
}
```

### Utilisation dans d'autres plugins

Ce nouveau type de champ peut être utilisé dans d'autres plugins d'actions qui ont besoin de référencer une variable du test :

```python
{
    "name": "source_variable",
    "type": "select-var-test",
    "label": "Variable source",
    "placeholder": "Sélectionnez une variable",
    "required": True
}
```

## Exemples d'utilisation

### Exemple 1 : Convertir un code HTTP en entier

**Contexte** : Après une requête HTTP, vous avez stocké le status code dans la variable `http_status` (string) et vous voulez le convertir en int pour faire des comparaisons.

**Configuration** :
- variable_name : `http_status`
- target_type : `int`
- output_mapping : `status_code` → `http_status_int`

**Résultat** :
```
"200" → 200 (int)
```

### Exemple 2 : Parser une réponse JSON

**Contexte** : Vous avez récupéré un JSON en string et voulez le convertir en dictionnaire.

**Configuration** :
- variable_name : `api_response`
- target_type : `dict`
- output_mapping : `converted_value` → `response_data`

**Résultat** :
```
'{"user_id": 123, "name": "John"}' → {"user_id": 123, "name": "John"}
```

### Exemple 3 : Convertir un flag en booléen

**Contexte** : Une API retourne `"true"` ou `"false"` en string.

**Configuration** :
- variable_name : `is_active_flag`
- target_type : `bool`
- output_mapping : `converted_value` → `is_active`

**Résultat** :
```
"true" → True
"false" → False
```

### Exemple 4 : Créer une liste à partir d'une string

**Contexte** : Vous avez un tableau JSON en string et voulez le manipuler.

**Configuration** :
- variable_name : `user_ids_json`
- target_type : `list`
- output_mapping : `converted_value` → `user_ids`

**Résultat** :
```
"[1, 2, 3, 4, 5]" → [1, 2, 3, 4, 5]
```

## Scénario complet d'utilisation

### Scénario : Validation d'une API REST

```
1. Action HTTP (GET /api/user/123)
   → Stocke la réponse dans la variable "api_response"
   
2. Action VarAction
   - variable_name : api_response
   - target_type : dict
   - output_mapping : converted_value → user_data
   
3. Action VarAction
   - variable_name : user_data.age  (extrait depuis le dict)
   - target_type : int
   - output_mapping : converted_value → user_age
   
4. Assertions sur user_age (int)
   - Vérifier que user_age > 18
```

## Gestion des erreurs

Le plugin retourne un code d'erreur (`1`) dans les cas suivants :

### Variable inexistante
```
❌ ERREUR : Variable 'my_var' introuvable
```

### Conversion impossible
```
❌ ERREUR de conversion : invalid literal for int() with base 10: 'abc'
```

### Type incompatible
```
❌ ERREUR : Impossible de convertir str en dictionnaire
```

## Logs d'exécution

Le plugin génère des logs détaillés :

```
Conversion de la variable 'http_status' vers le type 'int'
Valeur originale : 200 (type: str)
✅ Conversion réussie : 200 (type: int)
```

En cas d'erreur :
```
Conversion de la variable 'user_data' vers le type 'dict'
Valeur originale : not a json (type: str)
❌ ERREUR de conversion : Expecting value: line 1 column 1 (char 0)
```

## Tests unitaires

Le plugin est livré avec une suite de tests complète (`_build/test_var_action.py`) qui valide :

- ✅ Métadonnées du plugin
- ✅ Masque de saisie avec le nouveau type `select-var-test`
- ✅ Variables de sortie
- ✅ Validation de configuration
- ✅ Conversion vers int
- ✅ Conversion vers float
- ✅ Conversion vers bool (avec gestion intelligente des strings)
- ✅ Conversion vers list
- ✅ Conversion vers dict
- ✅ Conversion vers JSON
- ✅ Gestion des cas d'erreur

Pour exécuter les tests :
```bash
python3 _build/test_var_action.py
```

## Intégration avec l'interface utilisateur

Le plugin VarAction apparaît automatiquement dans l'interface :

1. **Dans le select des types d'actions** : "Variables (Conversion)"
2. **Formulaire dynamique** : 
   - Liste déroulante des variables du test
   - Liste déroulante des types cibles
3. **Variables de sortie** : Badge vert "converted_value" disponible pour mapping

## Compatibilité

- ✅ Compatible avec tous les plugins d'actions existants
- ✅ Supporte le mécanisme de variables de sortie
- ✅ S'intègre au système d'autocomplétion des variables
- ✅ Compatible avec l'exécution de campagnes

## Recommandations

1. **Toujours vérifier le type source** : Assurez-vous que la variable source contient un type compatible avec la conversion souhaitée
2. **Gérer les erreurs** : Utilisez le code de retour pour détecter les échecs de conversion
3. **Utiliser les logs** : Les logs détaillent chaque étape de la conversion
4. **Mapper les résultats** : Utilisez le mapping de variables de sortie pour utiliser la valeur convertie dans les actions suivantes

## Évolutions futures possibles

- [ ] Support de conversions personnalisées (ex: date/time)
- [ ] Validation de format (ex: email, URL)
- [ ] Opérations mathématiques (arrondi, abs, etc.)
- [ ] Transformations de strings (uppercase, lowercase, trim)
- [ ] Extraction de sous-éléments de structures complexes
