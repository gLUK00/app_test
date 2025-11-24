# Mesure des temps d'exécution dans les rapports

## Vue d'ensemble

Cette fonctionnalité permet de mesurer et d'afficher les temps d'exécution à trois niveaux :
- **Actions** : Temps de traitement de chaque action (en millisecondes)
- **Tests** : Temps total d'exécution de chaque test (en millisecondes)
- **Campagne** : Temps total d'exécution de la campagne (en millisecondes)

Les temps sont affichés dans l'interface de détails du rapport avec un formatage intelligent.

## Fonctionnalités

### 1. Mesure du temps d'exécution des actions

Chaque action d'un test a son temps d'exécution mesuré individuellement :

**Exemple de log :**
```
[10:30:15] Exécution de l'action 1/3: http
[10:30:16] ✅ Action réussie
[10:30:16] ⏱️ Temps d'exécution: 1245 ms
```

Les temps sont stockés dans un tableau `actionTimes` pour chaque test.

### 2. Mesure du temps d'exécution des tests

Le temps total d'un test inclut :
- Le temps de toutes les actions
- Le temps de résolution des variables
- Le temps de traitement des résultats

**Exemple de log :**
```
[10:30:18] ✅ Test terminé avec succès
[10:30:18] ⏱️ Temps total d'exécution du test: 3456 ms
```

### 3. Mesure du temps d'exécution de la campagne

Le temps total d'une campagne inclut :
- Le temps de tous les tests
- Le temps d'initialisation
- Le temps de finalisation

Le temps est affiché dans l'en-tête du rapport.

### 4. Formatage intelligent des temps

La fonction `formatExecutionTime()` affiche les temps de manière lisible :

| Durée | Affichage | Exemple |
|-------|-----------|---------|
| < 1 seconde | `X ms` | `450 ms` |
| 1s - 60s | `X.XX s` | `12.45 s` |
| >= 60s | `X min Y s` | `2 min 34 s` |

## Architecture technique

### Base de données

**Collection `rapports` - Nouveaux champs :**
```javascript
{
  _id: ObjectId,
  campainId: ObjectId,
  dateCreated: Date,
  // ... champs existants ...
  executionTimeMs: Number,  // Temps total en ms
  startTime: Number,        // Timestamp de début
  endTime: Number,          // Timestamp de fin
  tests: [{
    testId: ObjectId,
    status: String,
    logs: String,
    executionTimeMs: Number,  // Temps du test en ms
    actionTimes: [Number]     // Temps de chaque action en ms
  }]
}
```

### Module CampainExecutor

**Mesure du temps de la campagne :**
```python
def _run_campain(self, rapport_id, campain_id, filiere, tests, stop_on_failure):
    campain_start_time = time.time()  # Début
    
    # ... exécution de la campagne ...
    
    campain_end_time = time.time()
    campain_execution_time_ms = int((campain_end_time - campain_start_time) * 1000)
    
    Rapport.update(rapport_id, {
        'executionTimeMs': campain_execution_time_ms,
        'endTime': campain_end_time
    })
```

**Mesure du temps d'un test :**
```python
def _execute_test(self, test_id, variables_dict, filiere):
    test_start_time = time.time()
    action_times = []
    
    for action in actions:
        action_start_time = time.time()
        
        # Exécution de l'action
        result = action_plugin.execute(resolved_value)
        
        action_end_time = time.time()
        action_time_ms = int((action_end_time - action_start_time) * 1000)
        action_times.append(action_time_ms)
    
    test_end_time = time.time()
    test_execution_time_ms = int((test_end_time - test_start_time) * 1000)
    
    return {
        'testId': ObjectId(test_id),
        'status': status,
        'logs': '\n'.join(logs),
        'executionTimeMs': test_execution_time_ms,
        'actionTimes': action_times
    }
```

### Interface utilisateur

**Template rapport_details.html :**

1. **En-tête du rapport :**
```html
<div class="col-md-3">
    <p><strong>Temps d'exécution :</strong></p>
    <p class="fs-4 text-primary mb-0">
        <i class="fas fa-stopwatch"></i> <span id="rapportExecutionTime">-</span>
    </p>
</div>
```

2. **Liste des tests (accordion) :**
```html
<button class="accordion-button">
    <i class="fas ${statusIcon}"></i>
    Test ${index + 1} - ${statusText}
    <span class="ms-auto me-3 text-muted">
        <i class="fas fa-stopwatch"></i> ${executionTime}
    </span>
</button>
```

3. **Détails du test :**
```html
<div class="accordion-body">
    <div class="mb-3">
        <strong>Temps d'exécution:</strong> ${executionTime}
    </div>
    <h6>Logs d'exécution:</h6>
    <div class="test-log">${logs}</div>
</div>
```

**Fonction JavaScript de formatage :**
```javascript
function formatExecutionTime(milliseconds) {
    if (!milliseconds || milliseconds === 0) return '-';
    
    if (milliseconds < 1000) {
        return `${milliseconds} ms`;
    } else if (milliseconds < 60000) {
        const seconds = (milliseconds / 1000).toFixed(2);
        return `${seconds} s`;
    } else {
        const minutes = Math.floor(milliseconds / 60000);
        const seconds = ((milliseconds % 60000) / 1000).toFixed(0);
        return `${minutes} min ${seconds} s`;
    }
}
```

## Exemples de résultats

### Exemple 1 : Test rapide
```
Temps d'exécution de la campagne: 1.23 s
  └─ Test 1: 1.23 s
      ├─ Action 1 (HTTP GET): 450 ms
      ├─ Action 2 (Variable): 2 ms
      └─ Action 3 (HTTP POST): 780 ms
```

### Exemple 2 : Test long
```
Temps d'exécution de la campagne: 3 min 45 s
  ├─ Test 1: 1 min 20 s
  │   ├─ Action 1: 15.45 s
  │   ├─ Action 2: 45.20 s
  │   └─ Action 3: 19.35 s
  ├─ Test 2: 2 min 10 s
  └─ Test 3: 15 s
```

### Exemple 3 : Test avec actions rapides
```
Temps d'exécution de la campagne: 235 ms
  └─ Test 1: 235 ms
      ├─ Action 1 (Variable): 5 ms
      ├─ Action 2 (Conversion): 3 ms
      └─ Action 3 (Validation): 227 ms
```

## Logs d'exécution

Les logs affichent les temps avec l'icône ⏱️ :

```
[10:30:15] Démarrage du test
--------------------------------
[10:30:15] Exécution de l'action 1/3: http
[10:30:16] ✅ Action réussie
[10:30:16] ⏱️  Temps d'exécution: 1245 ms
--------------------------------
[10:30:16] Exécution de l'action 2/3: var
[10:30:16] ✅ Action réussie
[10:30:16] ⏱️  Temps d'exécution: 2 ms
--------------------------------
[10:30:16] Exécution de l'action 3/3: http
[10:30:18] ✅ Action réussie
[10:30:18] ⏱️  Temps d'exécution: 2209 ms
[10:30:18] ✅ Test terminé avec succès
[10:30:18] ⏱️  Temps total d'exécution du test: 3456 ms
```

## Cas d'usage

### Scénario 1 : Optimisation des performances
Identifiez les actions les plus lentes pour optimiser vos tests :
```
Action 1: 50 ms   ✅ Rapide
Action 2: 5000 ms ⚠️ Lente - à optimiser
Action 3: 100 ms  ✅ Rapide
```

### Scénario 2 : Validation des SLA
Vérifiez que vos tests respectent les temps de réponse attendus :
```
Temps d'exécution attendu: < 5s
Temps mesuré: 3.45 s ✅
```

### Scénario 3 : Détection des régressions
Comparez les temps d'exécution entre les rapports :
```
Rapport précédent: 2 min 30 s
Rapport actuel:    4 min 15 s ⚠️ Régression détectée
```

## Tests

### Script de test

Un script de test complet (`_build/test_execution_times.py`) valide :

**Exécution :**
```bash
python3 _build/test_execution_times.py
```

**Tests effectués :**
- ✅ Présence du champ `executionTimeMs` dans le rapport
- ✅ Présence des champs `startTime` et `endTime`
- ✅ Mise à jour correcte des temps
- ✅ Présence du champ `executionTimeMs` dans chaque test
- ✅ Présence du tableau `actionTimes`
- ✅ Cohérence des temps mesurés

## Migration des données existantes

Les rapports existants n'ont pas ces champs. Ils seront créés automatiquement lors de la prochaine exécution.

**Valeurs par défaut :**
```javascript
{
  executionTimeMs: 0,
  startTime: null,
  endTime: null
}
```

Les rapports existants afficheront `-` pour le temps d'exécution.

## Impacts sur l'existant

### ✅ Compatibilité assurée

- Les rapports existants continuent de fonctionner normalement
- L'affichage gère les cas où les temps ne sont pas disponibles (affiche `-`)
- Aucune modification des API publiques
- Pas de changement dans le format des logs existants

### Nouveaux comportements

- Les logs affichent maintenant les temps d'exécution
- L'interface affiche les temps dans l'en-tête et les détails
- Les données de temps sont persistées en base de données

## Performance

L'impact sur les performances est **négligeable** :
- Utilisation de `time.time()` : coût < 1 µs
- Calculs de temps : opérations arithmétiques simples
- Stockage : 3 nouveaux champs par rapport (12-24 bytes)

## Recommandations

1. **Surveiller les temps** : Utilisez cette fonctionnalité pour identifier les goulots d'étranglement
2. **Optimiser les actions lentes** : Actions > 5s méritent d'être optimisées
3. **Établir des baselines** : Comparez les temps entre les exécutions
4. **Documenter les temps attendus** : Ajoutez les temps cibles dans les descriptions

## Fichiers modifiés

- **models/rapport.py** : Ajout des champs de temps, mise à jour de create() et update()
- **utils/campain_executor.py** : Mesure des temps d'exécution
- **templates/rapport_details.html** : Affichage des temps d'exécution
- **_build/test_execution_times.py** : Script de test
- **docs/EXECUTION_TIMES.md** : Cette documentation
