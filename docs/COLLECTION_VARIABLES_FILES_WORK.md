# Nouvelles Variables de Collection - files_dir et work_dir

## Vue d'ensemble

Deux nouvelles variables de collection ont été ajoutées au système d'autocomplétion pour faciliter l'accès aux répertoires de travail des campagnes :

- **`{{test.files_dir}}`** : Chemin absolu vers le répertoire `files/` de la campagne
- **`{{test.work_dir}}`** : Chemin absolu vers le répertoire `work/` de la campagne

Ces variables permettent aux actions de tests d'accéder facilement aux fichiers de la campagne sans avoir à construire manuellement les chemins.

## Variables de Collection Disponibles

| Variable | Format d'insertion | Description |
|----------|-------------------|-------------|
| `test_id` | `{{test.test_id}}` | ID du test en cours d'exécution |
| `campain_id` | `{{test.campain_id}}` | ID de la campagne |
| `files_dir` | `{{test.files_dir}}` | Répertoire des fichiers de la campagne |
| `work_dir` | `{{test.work_dir}}` | Répertoire de travail de la campagne |

## Utilisation

### Dans l'Interface Utilisateur

Lors de la saisie des paramètres d'une action dans un test, le système d'autocomplétion propose automatiquement ces variables lorsque vous tapez `{{test.` :

```
{{test.   ← Déclenche l'autocomplétion
```

**Suggestions affichées** (en rouge, section "Variables de collection") :
- TEST_ID
- CAMPAIN_ID
- FILES_DIR ← Nouveau
- WORK_DIR ← Nouveau

### Exemples d'Utilisation

#### 1. Lire un fichier depuis le répertoire files/

**Action** : HTTPRequestAction ou IoAction

**Paramètre** : Chemin du fichier de configuration
```
{{test.files_dir}}/config.json
```

**Résultat lors de l'exécution** :
```
/home/user/app/workdir/507f1f77bcf86cd799439011/files/config.json
```

#### 2. Écrire un fichier dans le répertoire work/

**Action** : IoAction (écriture de fichier)

**Paramètre** : Chemin de sortie
```
{{test.work_dir}}/result.txt
```

**Résultat lors de l'exécution** :
```
/home/user/app/workdir/507f1f77bcf86cd799439011/work/result.txt
```

#### 3. Utiliser dans une URL WebDAV

**Action** : WebdavAction

**Paramètre** : URL source locale
```
file://{{test.files_dir}}/data_to_upload.csv
```

#### 4. Script SSH avec fichiers temporaires

**Action** : SSHAction

**Paramètre** : Commande
```
python3 /app/process.py --input {{test.files_dir}}/input.json --output {{test.work_dir}}/output.json
```

## Résolution des Variables

Lors de l'exécution d'une campagne, les variables sont résolues automatiquement :

### Exemple de Résolution

**Configuration de la campagne** :
- ID de campagne : `507f1f77bcf86cd799439011`
- workdir configuré : `./workdir`

**Variables résolues** :
```python
variables_dict = {
    'test.test_id': '507f191e810c19729de860ea',
    'test.campain_id': '507f1f77bcf86cd799439011',
    'test.files_dir': './workdir/507f1f77bcf86cd799439011/files',
    'test.work_dir': './workdir/507f1f77bcf86cd799439011/work'
}
```

**Texte avec variables** :
```
Lire le fichier {{test.files_dir}}/data.csv
```

**Après résolution** :
```
Lire le fichier ./workdir/507f1f77bcf86cd799439011/files/data.csv
```

## Structure des Répertoires

```
workdir/
└── {campain_id}/
    ├── files/      ← {{test.files_dir}}
    │   ├── config.json
    │   ├── data.csv
    │   └── script.sh
    └── work/       ← {{test.work_dir}}
        ├── temp1.txt
        └── output.log
```

## Cas d'Usage

### 1. Configuration Partagée

Stocker des fichiers de configuration dans `files/` et les référencer dans plusieurs tests :

**Fichier uploadé** : `config.json` dans la section Fichiers de la campagne

**Test 1 - Action HTTP** :
```json
{
  "url": "{{api_url}}/configure",
  "method": "POST",
  "body_file": "{{test.files_dir}}/config.json"
}
```

**Test 2 - Action SSH** :
```bash
scp {{test.files_dir}}/config.json user@server:/etc/myapp/
```

### 2. Fichiers Temporaires

Utiliser `work/` pour des fichiers temporaires générés pendant l'exécution :

**Test 1 - Générer des données** :
```python
# Action: Exécuter script Python
output_file = "{{test.work_dir}}/generated_data.json"
```

**Test 2 - Utiliser les données** :
```bash
# Action: SSH
cat {{test.work_dir}}/generated_data.json | curl -X POST {{api_url}}/import
```

### 3. Logs et Rapports

Sauvegarder des logs dans le répertoire de travail :

```bash
# Action: SSH - Exécuter un test de charge
wrk -t12 -c400 -d30s {{api_url}} > {{test.work_dir}}/load_test.log
```

Ensuite, télécharger le fichier depuis l'interface pour analyse.

## Différences entre files/ et work/

| Critère | files/ | work/ |
|---------|--------|-------|
| **Usage** | Fichiers uploadés manuellement | Fichiers générés automatiquement |
| **Visibilité** | Listés dans l'interface | Non listés (fichiers temporaires) |
| **Gestion** | Upload/Download/Delete via UI | Gestion par les actions uniquement |
| **Persistance** | Permanent (jusqu'à suppression) | Temporaire (nettoyé avec la campagne) |
| **Exemples** | Configs, scripts, données de test | Logs, résultats temporaires, cache |

## Avantages

### 1. **Portabilité**
Les tests ne dépendent plus de chemins absolus codés en dur. Ils fonctionnent sur n'importe quel environnement.

**Avant** :
```
/home/user/app/workdir/507f1f77bcf86cd799439011/files/config.json
```

**Après** :
```
{{test.files_dir}}/config.json
```

### 2. **Maintenabilité**
Si le chemin du workdir change, les tests continuent de fonctionner sans modification.

### 3. **Clarté**
Les variables explicites rendent les tests plus lisibles :
```
{{test.files_dir}}/input.csv  ← Clair et explicite
```

### 4. **Autocomplétion**
L'IDE vous aide à saisir correctement les variables avec suggestions et descriptions.

## Implémentation Technique

### Fichiers Modifiés

1. **`static/js/variable-autocomplete.js`**
   - Ajout de `files_dir` et `work_dir` dans `initCollectionVariables()`
   - Descriptions ajoutées pour l'autocomplétion

2. **`utils/campain_executor.py`**
   - Import de `get_campain_workdir` depuis `utils.workdir`
   - Calcul des chemins `files_dir` et `work_dir`
   - Ajout des variables dans `variables_dict`

### Code Ajouté

**JavaScript (variable-autocomplete.js)** :
```javascript
initCollectionVariables() {
    this.setVariables('collection', [
        { key: 'test_id', description: 'ID du test en cours' },
        { key: 'campain_id', description: 'ID de la campagne' },
        { key: 'files_dir', description: 'Répertoire des fichiers de la campagne' },
        { key: 'work_dir', description: 'Répertoire de travail de la campagne' }
    ]);
}
```

**Python (campain_executor.py)** :
```python
# Récupérer les chemins du workdir de la campagne
campain_workdir = Path(get_campain_workdir(campain_id))
files_dir = str(campain_workdir / "files")
work_dir = str(campain_workdir / "work")

# Ajouter les variables de collection
variables_dict['test.test_id'] = None
variables_dict['test.campain_id'] = campain_id
variables_dict['test.files_dir'] = files_dir
variables_dict['test.work_dir'] = work_dir
```

## Tests

Un script de test complet a été créé : `_build/test_collection_variables.py`

**Exécution** :
```bash
python3 _build/test_collection_variables.py
```

**Tests effectués** :
- ✅ Présence des variables dans l'autocomplétion JavaScript
- ✅ Descriptions des variables
- ✅ Import de `get_campain_workdir` dans campain_executor
- ✅ Assignation des variables dans `variables_dict`
- ✅ Format de résolution correct
- ✅ Format d'insertion `{{test.xxx}}`

## Compatibilité

### Rétrocompatibilité

Les tests existants continuent de fonctionner sans modification. Les nouvelles variables sont simplement ajoutées au dictionnaire de variables disponibles.

### Impact sur l'Existant

✅ **Aucun impact négatif** :
- Les tests existants ne sont pas affectés
- Les variables existantes (`test.test_id`, `test.campain_id`) fonctionnent toujours
- Pas de changement dans l'API ou les modèles de données

### Migration

**Aucune migration nécessaire**. Les tests existants peuvent être progressivement mis à jour pour utiliser les nouvelles variables si souhaité.

## Limitations

1. **Chemins absolus uniquement** : Les variables retournent des chemins absolus, pas relatifs
2. **Read-only** : Les variables sont en lecture seule pendant l'exécution
3. **Existence des répertoires** : Les répertoires doivent exister (créés automatiquement lors de la création de la campagne)

## Prochaines Étapes

### Évolutions Possibles

- [ ] Ajouter `test.campain_name` pour le nom de la campagne
- [ ] Ajouter `test.environment` pour l'environnement/filière
- [ ] Ajouter `test.rapport_id` pour l'ID du rapport en cours
- [ ] Permettre la création dynamique de sous-répertoires

## Documentation Associée

- `docs/VARIABLE_AUTOCOMPLETE_MULTITYPE.md` - Documentation de l'autocomplétion multi-types
- `docs/FILES_MANAGEMENT.md` - Documentation de la gestion des fichiers
- `docs/CAMPAIN_EXECUTION_README.md` - Documentation de l'exécution des campagnes

## Support

En cas de problème :
1. Vérifier que le workdir est correctement configuré dans `configuration.json`
2. Vérifier que les répertoires `files/` et `work/` existent dans le workdir de la campagne
3. Exécuter le script de test : `python3 _build/test_collection_variables.py`
4. Consulter les logs d'exécution de la campagne
