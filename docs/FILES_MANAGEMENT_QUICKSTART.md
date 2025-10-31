# Guide de Test Rapide - Gestion des Fichiers

## Pré-requis

1. **Démarrer l'application** :
   ```bash
   cd /home/hidalgo/Documents/projects/app_test
   python3 app.py
   ```

2. **Ouvrir le navigateur** sur `http://localhost:5000`

## Test Manuel - Interface Utilisateur

### 1. Connexion
- Email : `admin@example.com`
- Password : `admin123`

### 2. Créer une campagne de test
- Cliquer sur "Ajouter une campagne"
- Nom : `Test Gestion Fichiers`
- Description : `Campagne pour tester l'upload de fichiers`
- Sauvegarder

### 3. Accéder à la campagne
- Cliquer sur la campagne créée dans le tableau de bord
- Vous devriez voir 3 sections :
  1. **Informations** (nom, description, etc.)
  2. **Fichiers** ← NOUVELLE SECTION
  3. **Tests de la campagne**

### 4. Vérifier la section Fichiers
✅ Doit afficher :
- Un tableau avec colonnes : Nom, Taille (Ko), Date de modification, Actions
- Message "Aucun fichier dans cette campagne" (car vide)
- Bouton "Ajouter un fichier" en haut à droite

### 5. Tester l'upload de fichier

#### Test 1 : Upload simple
1. Cliquer sur "Ajouter un fichier"
2. Sélectionner un fichier depuis votre ordinateur
3. Laisser le champ "Renommer" vide
4. Cliquer "Uploader"

**Résultat attendu** :
- ✅ Message de succès
- ✅ La modale se ferme
- ✅ Le fichier apparaît dans la liste
- ✅ Taille affichée en Ko (ex: 2.34)
- ✅ Date de modification affichée

#### Test 2 : Upload avec renommage
1. Cliquer sur "Ajouter un fichier"
2. Sélectionner un fichier
3. Saisir un nouveau nom dans "Renommer" (ex: `mon_fichier_test.txt`)
4. Cliquer "Uploader"

**Résultat attendu** :
- ✅ Le fichier apparaît avec le nouveau nom

### 6. Tester le téléchargement
1. Cliquer sur le bouton "Télécharger" d'un fichier

**Résultat attendu** :
- ✅ Le fichier se télécharge dans votre dossier Téléchargements

### 7. Tester la suppression
1. Cliquer sur le bouton "Supprimer" d'un fichier
2. Confirmer la suppression

**Résultat attendu** :
- ✅ Boîte de confirmation affichée
- ✅ Après confirmation, message de succès
- ✅ Le fichier disparaît de la liste

### 8. Tester le WebSocket (rafraîchissement automatique)

**Setup** :
1. Ouvrir la page de la campagne dans 2 onglets différents
2. Dans l'onglet 1, uploader un fichier
3. Observer l'onglet 2

**Résultat attendu** :
- ✅ L'onglet 2 se rafraîchit automatiquement
- ✅ Le nouveau fichier apparaît sans recharger la page

## Test Automatisé - Script Python

```bash
cd /home/hidalgo/Documents/projects/app_test
python3 _build/test_files_management.py
```

**Ce script teste** :
- ✅ Authentification
- ✅ Création de campagne
- ✅ Structure du workdir (files/, work/)
- ✅ Upload de fichier
- ✅ Upload avec renommage
- ✅ Listing des fichiers
- ✅ Téléchargement de fichier
- ✅ Suppression de fichier
- ✅ Vérification de la suppression
- ✅ Nettoyage

**Résultat attendu** :
```
============================================================
Tests de la gestion des fichiers dans les campagnes
============================================================

[TEST] Authentification...
✓ Authentification réussie

[TEST] Création d'une campagne de test...
✓ Campagne créée avec l'ID: ...

[...]

============================================================
✓ Tous les tests sont passés avec succès!
============================================================
```

## Test API - cURL

### 1. Obtenir le token
```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")
```

### 2. Créer une campagne
```bash
CAMPAIN_ID=$(curl -s -X POST http://localhost:5000/api/campains \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test API","description":"Test via API"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['campain_id'])")
```

### 3. Lister les fichiers (vide)
```bash
curl -X GET "http://localhost:5000/api/campains/$CAMPAIN_ID/files" \
  -H "Authorization: Bearer $TOKEN"
```

**Résultat** : `{"files":[]}`

### 4. Upload un fichier
```bash
echo "Test content" > /tmp/test_file.txt

curl -X POST "http://localhost:5000/api/campains/$CAMPAIN_ID/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_file.txt"
```

**Résultat** : 
```json
{
  "message": "Fichier uploadé avec succès",
  "file": {
    "name": "test_file.txt",
    "size": 0.01,
    "modified": "2025-10-31T..."
  }
}
```

### 5. Lister les fichiers (avec fichier)
```bash
curl -X GET "http://localhost:5000/api/campains/$CAMPAIN_ID/files" \
  -H "Authorization: Bearer $TOKEN"
```

**Résultat** :
```json
{
  "files": [
    {
      "name": "test_file.txt",
      "size": 0.01,
      "modified": "2025-10-31T..."
    }
  ]
}
```

### 6. Télécharger un fichier
```bash
curl -X GET "http://localhost:5000/api/campains/$CAMPAIN_ID/files/test_file.txt" \
  -H "Authorization: Bearer $TOKEN" \
  -o /tmp/downloaded_file.txt
```

### 7. Supprimer un fichier
```bash
curl -X DELETE "http://localhost:5000/api/campains/$CAMPAIN_ID/files/test_file.txt" \
  -H "Authorization: Bearer $TOKEN"
```

**Résultat** : `{"message":"Fichier supprimé avec succès"}`

### 8. Nettoyer
```bash
curl -X DELETE "http://localhost:5000/api/campains/$CAMPAIN_ID" \
  -H "Authorization: Bearer $TOKEN"

rm /tmp/test_file.txt /tmp/downloaded_file.txt
```

## Vérification du Workdir

```bash
# Voir la structure
tree workdir/

# Devrait afficher :
# workdir/
# └── {campain_id}/
#     ├── files/
#     │   └── (vos fichiers uploadés)
#     └── work/
```

## Points de Contrôle

### ✅ Interface
- [ ] Section "Fichiers" visible entre Informations et Tests
- [ ] Tableau avec colonnes correctes
- [ ] Bouton "Ajouter un fichier" fonctionnel
- [ ] Modale s'ouvre/ferme correctement
- [ ] Upload fonctionne (avec et sans renommage)
- [ ] Téléchargement fonctionne
- [ ] Suppression fonctionne (avec confirmation)
- [ ] Messages de succès/erreur affichés

### ✅ API
- [ ] GET /files retourne la liste
- [ ] POST /files upload le fichier
- [ ] GET /files/{filename} télécharge
- [ ] DELETE /files/{filename} supprime
- [ ] Authentification requise
- [ ] Erreurs 404 si campagne/fichier inexistant

### ✅ WebSocket
- [ ] Connexion établie
- [ ] Join room fonctionne
- [ ] Événement files_updated émis après upload
- [ ] Événement files_updated émis après suppression
- [ ] Liste se rafraîchit automatiquement

### ✅ Système de Fichiers
- [ ] Répertoire workdir/{campain_id}/ créé
- [ ] Sous-répertoire files/ créé
- [ ] Sous-répertoire work/ créé
- [ ] Fichiers sauvegardés dans files/
- [ ] Noms de fichiers sécurisés
- [ ] Suppression de campagne nettoie le workdir

## Problèmes Connus

### Socket.IO "io is not defined"

**Problème résolu** : Socket.IO est maintenant inclus dans `templates/base.html` et disponible globalement.

Si vous rencontrez toujours l'erreur, vérifiez que :
1. Le fichier `/static/vendor/socket.io/socket.io.min.js` existe
2. La ligne `<script src="{{ url_for('static', filename='vendor/socket.io/socket.io.min.js') }}"></script>` est présente dans base.html

**Test rapide** : Ouvrez `http://localhost:5000/static/test-socketio.html` pour vérifier la connexion WebSocket.

### Environnement Virtuel
Si vous voyez des erreurs sur `webdav4` ou `eventlet`, c'est normal si vous utilisez le Python système. Pour un test complet :

```bash
source .venv/bin/activate  # Activer l'environnement virtuel
pip install -r requirements.txt
python3 app.py
```

### WebSocket en Mode Threading
L'application utilise le mode threading par défaut pour SocketIO. Pour de meilleures performances en production, installer eventlet :

```bash
pip install eventlet
```

Puis dans `app.py` :
```python
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
```

## Support

En cas de problème :
1. Vérifier les logs de l'application
2. Vérifier la console du navigateur (F12)
3. Consulter `docs/FILES_MANAGEMENT.md` pour plus de détails
4. Exécuter le script de test : `python3 _build/test_files_management.py`
