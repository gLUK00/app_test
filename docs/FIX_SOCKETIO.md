# Fix Socket.IO - "io is not defined"

## 🐛 Problème

Lors de l'ouverture de la page de détails d'une campagne, l'erreur suivante apparaissait dans la console du navigateur :

```
Uncaught ReferenceError: io is not defined
    at campain_details.html:xxx
```

Cette erreur empêchait le rafraîchissement automatique de la liste des fichiers via WebSocket.

## 🔍 Cause

La bibliothèque Socket.IO client (`socket.io.min.js`) n'était pas chargée dans le template `base.html`, ce qui rendait l'objet `io` indisponible pour les pages qui en avaient besoin.

## ✅ Solution

### 1. Ajout de Socket.IO dans base.html

**Fichier** : `templates/base.html`

Ajout de la ligne suivante dans la section des scripts, avant les scripts personnalisés :

```html
<!-- Socket.IO Client -->
<script src="{{ url_for('static', filename='vendor/socket.io/socket.io.min.js') }}"></script>
```

**Position complète** :
```html
<!-- Bootstrap JS -->
<script src="{{ url_for('static', filename='vendor/bootstrap/js/bootstrap.bundle.min.js') }}"></script>

<!-- Socket.IO Client -->
<script src="{{ url_for('static', filename='vendor/socket.io/socket.io.min.js') }}"></script>

<!-- Custom JS -->
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
<script src="{{ url_for('static', filename='js/variable-autocomplete.js') }}"></script>
```

### 2. Suppression du doublon dans rapport_details.html

**Fichier** : `templates/rapport_details.html`

Suppression de la ligne suivante (désormais inutile car Socket.IO est chargé globalement) :

```html
<!-- SUPPRIMÉ -->
<script src="{{ url_for('static', filename='vendor/socket.io/socket.io.min.js') }}"></script>
```

## 📋 Avantages de cette approche

1. **Chargement global** : Socket.IO est disponible sur toutes les pages
2. **Pas de doublon** : Un seul chargement de la bibliothèque
3. **Simplicité** : Pas besoin de l'inclure dans chaque page qui l'utilise
4. **Performance** : Mise en cache du fichier par le navigateur

## 🧪 Vérification

### Vérification automatique

Exécuter le script de vérification :
```bash
python3 _build/check_socketio.py
```

**Résultat attendu** :
```
============================================================
Vérification de la configuration Socket.IO
============================================================

📁 Fichiers requis:
✓ Bibliothèque Socket.IO client: static/vendor/socket.io/socket.io.min.js
✓ Template de base: templates/base.html
✓ Template de détails de campagne: templates/campain_details.html
✓ Page de test Socket.IO: static/test-socketio.html

📝 Configuration:
✓ Socket.IO chargé dans base.html
✓ Initialisation Socket.IO dans campain_details.html
✓ Gestionnaire join dans app.py
✓ Gestionnaire leave dans app.py
✓ Fonction emit_files_updated dans campains_routes.py

============================================================
✓ Tous les tests sont passés!
```

### Test dans le navigateur

1. **Démarrer l'application** :
   ```bash
   python3 app.py
   ```

2. **Ouvrir la page de test** :
   ```
   http://localhost:5000/static/test-socketio.html
   ```

   **Résultat attendu** :
   - ✅ Socket.IO est chargé
   - ✅ Connecté au serveur WebSocket
   - ✅ Aucune erreur dans la console

3. **Tester la fonctionnalité complète** :
   - Se connecter à l'application
   - Créer ou ouvrir une campagne
   - Ouvrir la console du navigateur (F12)
   - Vérifier qu'il n'y a **pas** d'erreur "io is not defined"
   - Uploader un fichier
   - Vérifier que la liste se rafraîchit automatiquement

### Vérification dans la console du navigateur

Ouvrir la console (F12) sur n'importe quelle page et taper :

```javascript
typeof io
```

**Résultat attendu** : `"function"` (et non `"undefined"`)

## 📝 Fichiers modifiés

```
✏️ templates/base.html
   + Ajout de la ligne Socket.IO client

✏️ templates/rapport_details.html
   - Suppression de la ligne Socket.IO (doublon)

📄 static/test-socketio.html
   + Création d'une page de test

📄 _build/check_socketio.py
   + Script de vérification automatique

📄 docs/FIX_SOCKETIO.md
   + Cette documentation
```

## 🎯 Impact

### Fonctionnalités maintenant opérationnelles

1. **Gestion des fichiers** :
   - ✅ Rafraîchissement automatique de la liste après upload
   - ✅ Rafraîchissement automatique de la liste après suppression
   - ✅ Synchronisation entre plusieurs onglets ouverts

2. **Exécution de campagnes** :
   - ✅ Mise à jour en temps réel du statut d'exécution
   - ✅ Logs en temps réel pendant l'exécution
   - ✅ Notification de fin d'exécution

### Avant/Après

**Avant** :
```
Page de campagne
  → Erreur console: "io is not defined"
  → Pas de rafraîchissement automatique
  → Besoin de recharger la page manuellement
```

**Après** :
```
Page de campagne
  → Socket.IO chargé correctement
  → Rafraîchissement automatique fonctionnel
  → Expérience utilisateur optimale
```

## 🚀 Prochaines étapes

La correction est maintenant complète et testée. Les utilisateurs peuvent :

1. Utiliser la gestion des fichiers avec rafraîchissement automatique
2. Suivre l'exécution des campagnes en temps réel
3. Bénéficier de la synchronisation multi-onglets

## 🔗 Documentation associée

- `docs/FILES_MANAGEMENT.md` - Documentation complète de la gestion des fichiers
- `docs/FILES_MANAGEMENT_QUICKSTART.md` - Guide de test rapide
- `docs/CAMPAIN_EXECUTION_README.md` - Documentation de l'exécution des campagnes
