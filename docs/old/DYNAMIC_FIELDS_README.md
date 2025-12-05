# Affichage dynamique des champs de saisie

## Modifications apportées

Cette mise à jour permet l'affichage dynamique des champs de saisie dans le formulaire d'ajout de test, en fonction du type de test sélectionné.

### Fichiers modifiés

1. **routes/actions_routes.py** (nouveau fichier)
   - Nouveau blueprint Flask pour exposer les masques de saisie via l'API
   - Endpoint `GET /api/actions/masks` : retourne tous les masques pour tous les types d'actions
   - Endpoint `GET /api/actions/masks/<type>` : retourne le masque pour un type d'action spécifique
   - Utilise la méthode `get_input_mask()` de chaque classe d'action

2. **routes/__init__.py**
   - Ajout de l'import du nouveau blueprint `actions_bp`
   - Ajout de `actions_bp` à la liste `__all__`

3. **app.py**
   - Import du blueprint `actions_bp`
   - Enregistrement du blueprint dans l'application Flask

4. **templates/test_add.html**
   - Suppression de tous les champs statiques spécifiques aux types de tests
   - Ajout d'une zone `<div id="dynamicFields"></div>` pour l'affichage dynamique
   - Ajout du JavaScript pour :
     - Charger les masques de saisie au chargement de la page
     - Afficher dynamiquement les champs selon le type sélectionné
     - Générer les champs HTML en fonction du masque (select, textarea, number, text)
     - Collecter et formater les données du formulaire lors de la soumission

5. **routes/auth_routes.py**
   - Ajout de la déclaration d'encodage UTF-8 en en-tête

### Fonctionnement

1. **Chargement de la page**
   - Au chargement, l'application appelle `/api/actions/masks` pour récupérer tous les masques
   - Les masques sont stockés dans la variable JavaScript `actionMasks`

2. **Sélection du type de test**
   - L'utilisateur sélectionne un type de test (HTTP, FTP, SFTP, SSH, WebDAV)
   - L'événement `change` déclenche l'affichage des champs correspondants
   - La zone `dynamicFields` est vidée puis remplie avec les champs appropriés

3. **Génération des champs**
   - Chaque champ du masque est converti en élément HTML
   - Types supportés : `select`, `textarea`, `number`, `string`
   - Les attributs `required`, `placeholder` sont appliqués automatiquement
   - Les labels indiquent si le champ est obligatoire (*)

4. **Soumission du formulaire**
   - Les valeurs sont collectées depuis les champs dynamiques
   - Les champs JSON (headers, body) sont parsés automatiquement
   - Les nombres sont convertis en entiers
   - Les données sont envoyées à l'API sous forme d'actions

### Types de champs disponibles

Chaque type d'action définit son propre masque de saisie via la méthode `get_input_mask()` :

- **HTTP** : method, url, headers, body
- **FTP** : method, host, port, username, password, remote_path, content
- **SFTP** : method, host, port, username, password, remote_path, content
- **SSH** : host, port, username, password, command
- **WebDAV** : method, url, username, password, headers, body

### Avantages

✅ **Extensibilité** : Ajouter un nouveau type d'action ne nécessite que l'implémentation de `get_input_mask()`
✅ **Cohérence** : Les champs affichés correspondent exactement aux besoins de chaque type d'action
✅ **UX améliorée** : L'utilisateur ne voit que les champs pertinents
✅ **Maintenance** : Un seul template pour tous les types de tests
✅ **Validation** : Les champs obligatoires sont automatiquement marqués

### Test

Pour tester le fonctionnement :

```bash
# Lancer le script de test
python3 test_dynamic_fields.py

# Ou démarrer l'application et tester manuellement
python3 app.py
```

Puis accéder à `/campains/<id>/add/test` et sélectionner différents types de tests pour voir les champs s'afficher dynamiquement.
