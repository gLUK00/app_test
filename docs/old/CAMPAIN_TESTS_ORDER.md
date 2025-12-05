# Gestion de l'ordre des tests dans une campagne

## Vue d'ensemble

Cette fonctionnalité permet de définir et gérer l'ordre d'exécution des tests au sein d'une campagne. Les tests sont maintenant exécutés dans un ordre spécifique que vous pouvez personnaliser.

## Fonctionnalités

### 1. Ordre automatique lors de la création

Lorsqu'un nouveau test est créé dans une campagne, il est automatiquement placé **à la fin** de la liste des tests existants avec un ordre séquentiel.

**Exemple:**
- Campagne avec 3 tests (ordre: 1, 2, 3)
- Nouveau test créé → ordre = 4

### 2. Réorganisation des tests

Dans la page de gestion d'une campagne (`/campains/:id`), chaque test dispose de boutons pour modifier son ordre d'exécution :

- **Bouton ↑ (Monter)** : Déplace le test d'une position vers le haut
- **Bouton ↓ (Descendre)** : Déplace le test d'une position vers le bas

**Limitations:**
- Le premier test ne peut pas monter (bouton désactivé)
- Le dernier test ne peut pas descendre (bouton désactivé)

### 3. Exécution dans l'ordre défini

Lors de l'exécution d'une campagne, les tests sont exécutés **dans l'ordre défini**, du plus petit ordre au plus grand.

**Exemple d'ordre d'exécution:**
```
Ordre 1: Test de connexion
Ordre 2: Test de création de données
Ordre 3: Test de modification
Ordre 4: Test de suppression
Ordre 5: Test de déconnexion
```

## Architecture technique

### Base de données

**Collection `tests` - Nouveau champ:**
```javascript
{
  _id: ObjectId,
  campainId: ObjectId,
  userId: ObjectId,
  name: String,
  description: String,
  actions: Array,
  variables: Array,
  dateCreated: Date,
  order: Number  // ← NOUVEAU CHAMP
}
```

### API Routes

**Nouvelles routes ajoutées:**

```
POST /api/tests/:id/move-up
```
Déplace un test vers le haut dans l'ordre d'exécution.

**Réponse en cas de succès (200):**
```json
{
  "message": "Test déplacé vers le haut avec succès"
}
```

**Réponse en cas d'échec (400):**
```json
{
  "message": "Impossible de déplacer le test (déjà en première position ou test introuvable)"
}
```

---

```
POST /api/tests/:id/move-down
```
Déplace un test vers le bas dans l'ordre d'exécution.

**Réponse en cas de succès (200):**
```json
{
  "message": "Test déplacé vers le bas avec succès"
}
```

**Réponse en cas d'échec (400):**
```json
{
  "message": "Impossible de déplacer le test (déjà en dernière position ou test introuvable)"
}
```

### Modèle Test

**Nouvelles méthodes:**

#### `Test.move_up(test_id)`
Déplace un test vers le haut en échangeant son ordre avec le test précédent.

**Retourne:**
- `True` si le déplacement a réussi
- `False` si le test est déjà en première position ou introuvable

#### `Test.move_down(test_id)`
Déplace un test vers le bas en échangeant son ordre avec le test suivant.

**Retourne:**
- `True` si le déplacement a réussi
- `False` si le test est déjà en dernière position ou introuvable

#### Modification de `Test.create()`
Attribue automatiquement un ordre = `max(ordres existants) + 1` au nouveau test.

#### Modification de `Test.get_by_campain()`
Trie maintenant les tests par ordre croissant (`sort('order', 1)`) au lieu de par date de création.

## Interface utilisateur

### Page de gestion de campagne

La liste des tests affiche maintenant des boutons de réorganisation :

```html
<button class="btn btn-sm btn-outline-secondary" onclick="moveTestUp(testId)">
  <i class="fas fa-arrow-up"></i>
</button>
<button class="btn btn-sm btn-outline-secondary" onclick="moveTestDown(testId)">
  <i class="fas fa-arrow-down"></i>
</button>
```

Les boutons sont désactivés automatiquement selon la position :
- Premier test : bouton ↑ désactivé
- Dernier test : bouton ↓ désactivé

### Fonctions JavaScript

**`moveTestUp(testId)`**
```javascript
async function moveTestUp(testId) {
    await API.post(`/api/tests/${testId}/move-up`, {});
    loadTests(); // Recharge la liste
}
```

**`moveTestDown(testId)`**
```javascript
async function moveTestDown(testId) {
    await API.post(`/api/tests/${testId}/move-down`, {});
    loadTests(); // Recharge la liste
}
```

## Migration des données existantes

### Script de migration

Un script de migration (`_build/migrate_tests_order.py`) a été créé pour ajouter le champ `order` aux tests existants.

**Exécution:**
```bash
python3 _build/migrate_tests_order.py
```

**Ce que fait le script:**
1. Parcourt toutes les campagnes
2. Pour chaque campagne, récupère ses tests
3. Trie les tests par date de création (du plus ancien au plus récent)
4. Attribue un ordre séquentiel (1, 2, 3, ...) aux tests sans ordre
5. Conserve l'ordre existant si déjà défini

## Tests

### Script de test

Un script de test complet (`_build/test_campain_order.py`) valide toutes les fonctionnalités :

**Exécution:**
```bash
python3 _build/test_campain_order.py
```

**Tests effectués:**
- ✅ Création de tests avec ordre automatique
- ✅ Tri des tests par ordre
- ✅ Déplacement vers le haut (`move_up`)
- ✅ Déplacement vers le bas (`move_down`)
- ✅ Limites (premier/dernier test)
- ✅ Persistance de l'ordre

## Impacts sur l'existant

### ✅ Compatibilité assurée

La fonctionnalité a été conçue pour être **totalement compatible** avec l'existant :

1. **Tests existants sans ordre** : Le script de migration attribue automatiquement un ordre basé sur la date de création

2. **Méthode `Test.create()`** : Gère automatiquement l'ordre, pas d'impact sur le code existant

3. **Méthode `Test.get_by_campain()`** : Modification transparente du tri (par ordre au lieu de par date)

4. **Exécution de campagnes** : Aucune modification nécessaire dans `CampainExecutor`, l'ordre est géré au niveau du modèle

5. **Interface utilisateur** : Ajout de boutons sans impact sur les fonctionnalités existantes

### ⚠️ Points d'attention

- **Ordre par défaut** : Les nouveaux tests sont toujours placés à la fin
- **Migration requise** : Exécuter le script de migration pour les données existantes
- **Tri modifié** : La liste des tests est maintenant triée par ordre et non plus par date

## Cas d'usage

### Scénario 1 : Tests de bout en bout
```
1. Test de connexion
2. Test de création de compte
3. Test de modification de profil
4. Test de déconnexion
```

### Scénario 2 : Tests de dépendances
```
1. Création de données de base
2. Test utilisant les données créées
3. Modification des données
4. Suppression des données
5. Vérification de la suppression
```

### Scénario 3 : Réorganisation
Si vous devez ajouter un test au milieu :
1. Créer le nouveau test (ajouté à la fin)
2. Utiliser les boutons ↑ pour le déplacer à la position souhaitée

## Logs et débogage

Les logs de déplacement sont visibles dans :
- Console navigateur (appels API)
- Notifications utilisateur (succès/erreur)

**Exemple de log:**
```
✓ Test déplacé vers le haut
```

## Recommandations

1. **Planifier l'ordre dès le départ** : Pensez à la logique d'exécution avant de créer les tests
2. **Tester l'ordre** : Vérifiez l'ordre d'exécution avant de lancer une campagne importante
3. **Documenter les dépendances** : Si des tests dépendent d'autres, documentez-le dans la description
4. **Migration** : Exécutez le script de migration avant d'utiliser la fonctionnalité sur des données existantes

## Fichiers modifiés

- **models/test.py** : Ajout du champ `order`, méthodes `move_up()`, `move_down()`
- **routes/tests_routes.py** : Nouvelles routes `/move-up` et `/move-down`
- **templates/campain_details.html** : Ajout des boutons et fonctions JS
- **_build/test_campain_order.py** : Script de test
- **_build/migrate_tests_order.py** : Script de migration
- **docs/CAMPAIN_TESTS_ORDER.md** : Cette documentation
