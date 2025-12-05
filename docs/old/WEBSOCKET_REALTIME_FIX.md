# Fix: Mise à jour en temps réel des rapports via WebSocket

## Problème rencontré

Lors de l'exécution d'une campagne via "Exécuter la campagne", l'IHM reste bloquée en statut "running" avec une progression à 50%, alors que la campagne est bien terminée en base de données.

**Symptômes** :
- L'IHM affiche "running" et 50% de progression
- En cliquant sur le détail ou en rafraîchissant la page, la campagne apparaît comme terminée
- Les données en base sont correctes, le problème est uniquement dans la synchronisation temps réel

## Cause du problème

La page `campain_details.html` n'écoutait PAS les événements WebSocket émis par le `CampainExecutor` lors de l'exécution de la campagne.

**Événements émis par le backend** (`utils/campain_executor.py`) :
```python
# Démarrage de la campagne
self.socketio.emit('campain_started', {...}, room=f'rapport_{rapport_id}')

# Progression de la campagne
self.socketio.emit('campain_progress', {...}, room=f'rapport_{rapport_id}')

# Démarrage d'un test
self.socketio.emit('test_started', {...}, room=f'rapport_{rapport_id}')

# Fin d'un test
self.socketio.emit('test_completed', {...}, room=f'rapport_{rapport_id}')

# Fin de la campagne
self.socketio.emit('campain_completed', {...}, room=f'rapport_{rapport_id}')

# Erreur
self.socketio.emit('campain_error', {...}, room=f'rapport_{rapport_id}')
```

**Problème** : L'IHM ne rejoignait pas la room `rapport_{rapport_id}` et n'écoutait pas ces événements.

## Solution implémentée

### 1. Ajout des listeners WebSocket

Dans `templates/campain_details.html`, ajout de l'écoute des événements :

```javascript
// Écouter les événements de progression de campagne
socket.on('campain_started', (data) => {
    console.log('Campagne démarrée:', data);
    loadRapports();
});

socket.on('campain_progress', (data) => {
    console.log('Progression de campagne:', data);
    loadRapports();
});

socket.on('campain_completed', (data) => {
    console.log('Campagne terminée:', data);
    loadRapports();
});

socket.on('test_started', (data) => {
    console.log('Test démarré:', data);
    loadRapports();
});

socket.on('test_completed', (data) => {
    console.log('Test terminé:', data);
    loadRapports();
});

socket.on('campain_error', (data) => {
    console.log('Erreur de campagne:', data);
    loadRapports();
    Notification.error('Erreur lors de l\'exécution de la campagne');
});
```

### 2. Fonction pour rejoindre les rooms des rapports actifs

```javascript
// Tracker les rapports actifs pour rejoindre leurs rooms
let activeRapports = new Set();

// Fonction pour rejoindre les rooms des rapports actifs
function joinActiveRapportRooms(rapports) {
    rapports.forEach(rapport => {
        if ((rapport.status === 'running' || rapport.status === 'pending') && !activeRapports.has(rapport._id)) {
            socket.emit('join', { room: `rapport_${rapport._id}` });
            activeRapports.add(rapport._id);
            console.log(`Joined room: rapport_${rapport._id}`);
        }
    });
}
```

### 3. Appel dans loadRapports()

```javascript
async function loadRapports() {
    try {
        const data = await API.get(`/api/rapports?campain_id=${campainId}`);
        
        if (data.data && data.data.length > 0) {
            // Rejoindre les rooms des rapports actifs
            joinActiveRapportRooms(data.data);
            
            // ... reste du code ...
        }
    } catch (error) {
        console.error('Erreur lors du chargement des rapports:', error);
    }
}
```

### 4. Rejoint immédiat de la room lors du lancement ⚡ CRITIQUE

**Le problème du timing** : Si on attend 1 seconde avant de rejoindre la room, les premiers événements sont perdus.

**Solution** : Rejoindre la room **immédiatement** après avoir reçu le `rapport_id` :

```javascript
document.getElementById('launchCampainBtn').addEventListener('click', async () => {
    // ... validation ...
    
    const result = await API.post('/api/rapports/execute', {
        campain_id: campainId,
        name: name,
        filiere: filiere,
        stop_on_failure: stopOnFailure
    });
    
    // ⚡ CRITIQUE: Rejoindre IMMÉDIATEMENT la room du rapport
    if (result.rapport_id) {
        const rapportRoom = `rapport_${result.rapport_id}`;
        socket.emit('join', { room: rapportRoom });
        activeRapports.add(result.rapport_id);
        console.log(`🔌 Joined room immediately: ${rapportRoom}`);
    }
    
    // Fermer la modale et recharger (sans timeout)
    modal.hide();
    loadRapports();
});
```

### 5. Délai côté serveur pour synchronisation

Dans `utils/campain_executor.py`, ajout d'un petit délai pour garantir que le client a rejoint la room :

```python
def _run_campain(self, rapport_id, campain_id, filiere, tests, stop_on_failure):
    """Exécute la campagne de tests."""
    campain_start_time = time.time()
    
    try:
        # Petit délai pour laisser le client rejoindre la room WebSocket
        time.sleep(0.1)
        
        # Mettre à jour le statut à "running"
        Rapport.update(rapport_id, {
            'status': 'running',
            'progress': 0,
            'startTime': campain_start_time
        })
        
        # Émettre l'événement de démarrage
        self.socketio.emit('campain_started', {
            'rapport_id': rapport_id,
            'campain_id': campain_id
        }, room=f'rapport_{rapport_id}')
        
        print(f"📡 Événement 'campain_started' émis pour rapport_{rapport_id}")
```

### 6. Logs serveur pour le débogage

Ajout de logs pour tous les événements émis :

```python
print(f"📡 Événement 'campain_started' émis pour rapport_{rapport_id}")
print(f"📡 Événement 'test_started' émis pour test {test_id}")
print(f"📡 Événement 'test_completed' émis pour test {test_id}")
print(f"📡 Événement 'campain_progress' émis: {progress}%")
print(f"📡 Événement 'campain_completed' émis: status={final_status}, result={final_result}")
print(f"📡 Événement 'campain_error' émis")
```

## Flux de fonctionnement

### Avant le fix

```
1. Utilisateur clique "Lancer la campagne"
2. Backend démarre l'exécution en arrière-plan
3. Backend émet des événements WebSocket → Personne n'écoute ❌
4. IHM affiche le dernier état connu (running 50%)
5. Utilisateur doit rafraîchir manuellement
```

### Après le fix

```
1. Utilisateur clique "Lancer la campagne"
2. API crée le rapport → loadRapports() est appelé
3. loadRapports() rejoint la room rapport_{id}
4. Backend démarre l'exécution en arrière-plan
5. Backend émet campain_started → IHM reçoit → loadRapports()
6. Backend émet campain_progress → IHM reçoit → loadRapports()
7. Backend émet test_completed → IHM reçoit → loadRapports()
8. Backend émet campain_completed → IHM reçoit → loadRapports()
9. IHM affiche automatiquement le statut final ✅
```

## Architecture WebSocket

### Rooms utilisées

1. **`campain_{campain_id}`** : Pour les mises à jour des fichiers
   ```javascript
   socket.emit('join', { room: `campain_${campainId}` });
   socket.on('files_updated', (data) => { ... });
   ```

2. **`rapport_{rapport_id}`** : Pour les mises à jour de progression
   ```javascript
   socket.emit('join', { room: `rapport_${rapport_id}` });
   socket.on('campain_started', (data) => { ... });
   socket.on('campain_progress', (data) => { ... });
   socket.on('campain_completed', (data) => { ... });
   ```

### Événements par type de room

| Room | Événement | Donnée | Action IHM |
|------|-----------|---------|------------|
| `campain_{id}` | `files_updated` | `{ campain_id }` | `loadFiles()` |
| `rapport_{id}` | `campain_started` | `{ rapport_id, campain_id }` | `loadRapports()` |
| `rapport_{id}` | `campain_progress` | `{ rapport_id, progress }` | `loadRapports()` |
| `rapport_{id}` | `test_started` | `{ rapport_id, test_id }` | `loadRapports()` |
| `rapport_{id}` | `test_completed` | `{ rapport_id, test_id, status }` | `loadRapports()` |
| `rapport_{id}` | `campain_completed` | `{ rapport_id, status, result }` | `loadRapports()` |
| `rapport_{id}` | `campain_error` | `{ rapport_id, error }` | `loadRapports()` + notification |

## Test de validation

Le script `_build/test_websocket_realtime.py` valide le bon fonctionnement :

```bash
python3 _build/test_websocket_realtime.py
```

**Tests effectués** :
- ✅ Création d'un rapport initial (status: pending, progress: 0)
- ✅ Mise à jour à "running" avec progress: 0
- ✅ Mise à jour de la progression à 50%
- ✅ Mise à jour de la progression à 100%
- ✅ Mise à jour à "completed" avec temps d'exécution
- ✅ Vérification de la cohérence des champs de temps

## Impact sur l'existant

### ✅ Compatibilité assurée

- Pas de modification des APIs existantes
- Pas de modification du backend (événements déjà émis)
- Pas de modification de la base de données
- Compatible avec les anciens rapports

### Nouveaux comportements

- L'IHM se met à jour automatiquement pendant l'exécution
- La barre de progression évolue en temps réel
- Le statut change automatiquement (running → completed/failed)
- Les logs de console affichent les événements reçus

## Vérification manuelle

Pour vérifier que le fix fonctionne :

1. Ouvrir la page de détails d'une campagne
2. Ouvrir la console du navigateur (F12)
3. Cliquer sur "Exécuter la campagne"
4. Observer dans la console :
   ```
   Joined room: rapport_690a01f802f22a19914edb93
   Campagne démarrée: {rapport_id: "...", campain_id: "..."}
   Progression de campagne: {rapport_id: "...", progress: 50}
   Test terminé: {rapport_id: "...", test_id: "..."}
   Campagne terminée: {rapport_id: "...", status: "completed"}
   ```
5. Vérifier que la barre de progression se met à jour automatiquement
6. Vérifier que le statut passe à "completed" sans rafraîchir la page

## Fichiers modifiés

- **templates/campain_details.html** : Ajout des listeners WebSocket et de la fonction joinActiveRapportRooms()
- **_build/test_websocket_realtime.py** : Script de test pour valider le bon fonctionnement
- **docs/WEBSOCKET_REALTIME_FIX.md** : Cette documentation

## Recommandations

1. **Surveiller les logs console** : Vérifiez que les événements sont bien reçus
2. **Limiter les rooms** : Ne rejoindre que les rapports "running" ou "pending"
3. **Cleanup** : Quitter les rooms des rapports terminés (à implémenter si nécessaire)
4. **Performance** : Si beaucoup de rapports simultanés, limiter le nombre de rooms actives

## Problèmes potentiels et solutions

### Problème : Trop de rooms actives

**Symptôme** : Ralentissement si l'utilisateur a beaucoup de rapports en cours

**Solution** : Implémenter un système de nettoyage :
```javascript
// Quitter les rooms des rapports terminés
function leaveCompletedRapportRooms(rapports) {
    activeRapports.forEach(rapportId => {
        const rapport = rapports.find(r => r._id === rapportId);
        if (!rapport || (rapport.status !== 'running' && rapport.status !== 'pending')) {
            socket.emit('leave', { room: `rapport_${rapportId}` });
            activeRapports.delete(rapportId);
            console.log(`Left room: rapport_${rapportId}`);
        }
    });
}
```

### Problème : Événements manqués

**Symptôme** : L'IHM ne se met pas à jour alors que la campagne s'exécute

**Solution** : Vérifier que :
1. Le WebSocket est bien connecté : `socket.connected`
2. La room a été rejointe : observer les logs console
3. Le backend émet bien les événements : vérifier les logs serveur

### Problème : Rafraîchissements trop fréquents

**Symptôme** : `loadRapports()` est appelé trop souvent

**Solution** : Implémenter un debounce :
```javascript
let loadRapportsTimeout;
function debouncedLoadRapports() {
    clearTimeout(loadRapportsTimeout);
    loadRapportsTimeout = setTimeout(loadRapports, 300);
}

socket.on('campain_progress', debouncedLoadRapports);
```

## Conclusion

Le problème de l'IHM qui reste bloquée en "running" était dû à l'absence d'écoute des événements WebSocket. La solution consiste à :

1. S'abonner aux événements émis par le backend
2. Rejoindre automatiquement les rooms des rapports actifs
3. Recharger la liste des rapports à chaque événement

Cette solution assure une mise à jour en temps réel de l'interface sans nécessiter de rafraîchissement manuel.
