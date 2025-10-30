# Implémentation du système d'exécution de campagnes en temps réel

## 🎯 Fonctionnalités implémentées

### 1. Formulaire de lancement de campagne
✅ **Modale d'exécution** dans `campain_details.html` avec:
- Nom du rapport auto-généré (format: "Mois Année")
- Gestion automatique de l'unicité avec suffixe numérique (ex: "Mars 2023 (1)")
- Sélection de l'environnement (liste des filières)
- Case à cocher "Arrêter au premier échec"
- Boutons "Lancer la campagne" et "Annuler"
- Validation: nom et environnement obligatoires

### 2. Exécution en arrière-plan
✅ **Nouveau module** `utils/campain_executor.py`:
- Classe `CampainExecutor` pour gérer l'exécution
- Exécution dans un thread séparé (non bloquant)
- Support de toutes les actions via le PluginManager
- Résolution des variables (TestGyver, test, collection)
- Capture des variables de sortie des actions
- Génération de logs horodatés

### 3. Modèle de données étendu
✅ **Modèle Rapport** (`models/rapport.py`) avec nouveaux champs:
- `status`: 'pending', 'running', 'completed', 'failed'
- `progress`: pourcentage (0-100)
- `stopOnFailure`: stratégie d'arrêt
- Méthode `get_by_name()` pour vérifier l'unicité

✅ **Modèle Variable** (`models/variable.py`):
- Méthode `get_all_filieres()` pour lister les environnements

### 4. API REST
✅ **Nouvelles routes** dans `routes/rapports_routes.py`:
- `POST /api/rapports/execute`: Lance l'exécution
- `GET /api/rapports/generate-name`: Génère un nom unique
- `GET /api/rapports/filieres`: Liste des environnements

### 5. WebSocket en temps réel
✅ **Flask-SocketIO** configuré dans `app.py`:
- Support des événements bidirectionnels
- Mode async avec eventlet

✅ **Événements WebSocket** émis:
- `campain_started`: Début de l'exécution
- `test_started`: Début d'un test
- `test_completed`: Fin d'un test avec logs
- `campain_progress`: Mise à jour de progression
- `campain_completed`: Fin de l'exécution
- `campain_error`: Erreur système

### 6. Interface utilisateur

✅ **Page de détails de campagne** (`templates/campain_details.html`):
- Bouton "Exécuter la campagne" avec modale
- Liste des rapports avec:
  - Nom, date, environnement
  - Statut avec badge coloré et icône
  - Barre de progression animée
  - Bouton "Voir" pour les détails

✅ **Page de détails de rapport** (`templates/rapport_details.html`):
- Connexion WebSocket automatique
- Informations générales du rapport
- Liste des tests en accordéon
- Indicateur "Live" pendant l'exécution
- Mise à jour en temps réel:
  - Statuts des tests
  - Logs d'exécution
  - Progression globale
- Styles personnalisés pour les logs (console noire)

✅ **Route web** (`routes/web_routes.py`):
- `GET /rapports/<rapport_id>`: Page de détails

### 7. Résolution des variables
✅ **Trois types de variables supportés**:
- `{{variable}}`: Variables TestGyver (environnement)
- `{{app.variable}}`: Variables du test (sortie d'actions)
- `{{test.variable}}`: Variables de collection (test_id, campain_id)

### 8. Gestion des erreurs
✅ **Validation**:
- Nom de rapport unique
- Environnement valide
- Présence de tests dans la campagne

✅ **Stratégie d'arrêt**:
- Si "Arrêter au premier échec" est activé
- Tests restants marqués "skipped"
- Logs explicatifs

## 📦 Dépendances ajoutées

```
flask-socketio==5.3.4
python-socketio==5.10.0
eventlet==0.33.3
```

## 📁 Fichiers créés

1. `utils/campain_executor.py` - Moteur d'exécution
2. `templates/rapport_details.html` - Page de détails
3. `docs/CAMPAIN_EXECUTION_README.md` - Documentation complète
4. `_build/test_campain_execution.py` - Tests unitaires

## 📝 Fichiers modifiés

1. `requirements.txt` - Ajout des dépendances
2. `app.py` - Configuration SocketIO
3. `models/rapport.py` - Nouveaux champs
4. `models/variable.py` - Méthode get_all_filieres()
5. `routes/rapports_routes.py` - Nouvelles routes API
6. `routes/web_routes.py` - Route rapport_details
7. `templates/campain_details.html` - Modale et liste des rapports

## 🧪 Tests

Exécuter les tests:
```bash
python _build/test_campain_execution.py
```

Tests couverts:
- ✅ Génération de nom unique
- ✅ Résolution des variables
- ✅ Flux de statuts
- ✅ Calcul de progression
- ✅ Événements WebSocket

## 🚀 Utilisation

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Lancer l'application
L'application doit maintenant être lancée avec SocketIO:
```bash
python app.py
```

### 3. Exécuter une campagne

1. Accéder à une campagne: `/campains/<campain_id>`
2. Cliquer sur "Exécuter la campagne"
3. Remplir le formulaire:
   - Le nom est pré-rempli avec "Mois Année"
   - Sélectionner un environnement
   - Cocher "Arrêter au premier échec" si souhaité
4. Cliquer sur "Lancer la campagne"
5. Un rapport est créé et l'exécution démarre
6. Cliquer sur "Voir" pour suivre en temps réel

### 4. Suivre l'exécution

Dans la page de détails du rapport:
- L'indicateur "Live" s'affiche pendant l'exécution
- Les statuts des tests se mettent à jour automatiquement
- Les logs apparaissent en temps réel
- La barre de progression avance
- Notification à la fin de l'exécution

## 🔍 Architecture technique

```
Client (Browser)
    ↓ WebSocket
SocketIO Server (Flask-SocketIO)
    ↓
CampainExecutor (Thread)
    ↓
PluginManager → Actions
    ↓
MongoDB (Rapports, Tests, Variables)
```

## 📊 Flux de données

1. **Lancement**:
   - POST /api/rapports/execute
   - Création du rapport (status: pending)
   - Lancement du thread d'exécution
   - Retour immédiat avec rapport_id

2. **Exécution** (en arrière-plan):
   - Pour chaque test:
     - Émission `test_started`
     - Exécution des actions
     - Résolution des variables
     - Capture des logs
     - Émission `test_completed`
     - Émission `campain_progress`
   - Finalisation du rapport
   - Émission `campain_completed`

3. **Suivi** (en temps réel):
   - Connexion WebSocket
   - Réception des événements
   - Mise à jour du DOM
   - Défilement automatique des logs

## 🎨 Statuts visuels

| Statut    | Couleur | Icône            | Description              |
|-----------|---------|------------------|--------------------------|
| pending   | Gris    | fa-clock         | En attente               |
| running   | Bleu    | fa-spinner       | En cours d'exécution     |
| completed | Vert    | fa-check-circle  | Terminé avec succès      |
| failed    | Rouge   | fa-times-circle  | Terminé avec échecs      |
| passed    | Vert    | fa-check-circle  | Test réussi              |
| skipped   | Jaune   | fa-forward       | Test ignoré              |

## ✨ Fonctionnalités clés

### Nom de rapport intelligent
```javascript
// Génération automatique avec gestion d'unicité
"Mars 2023" → existe
"Mars 2023 (1)" → existe
"Mars 2023 (2)" → OK ✓
```

### Variables multi-niveaux
```javascript
// Dans une action HTTP:
{
  "url": "{{api_url}}/users/{{app.user_id}}",
  "headers": {
    "X-Test-ID": "{{test.test_id}}",
    "X-Campain-ID": "{{test.campain_id}}"
  }
}
```

### Logs en temps réel
```
[10:30:15] Démarrage du test
[10:30:16] Exécution de l'action 1/3: HTTPRequestAction
[10:30:17] ✅ Action réussie
[10:30:17] 📝 Variable 'user_id' = 12345
[10:30:18] ✅ Test terminé avec succès
```

## 📖 Documentation

Consulter `docs/CAMPAIN_EXECUTION_README.md` pour:
- Architecture détaillée
- Exemples d'utilisation
- API complète
- Gestion des erreurs
- Notes techniques

## ✅ Checklist d'implémentation

- [x] Installer Flask-SocketIO
- [x] Configurer WebSocket dans app.py
- [x] Étendre le modèle Rapport
- [x] Créer CampainExecutor
- [x] Implémenter les routes API
- [x] Créer la modale de lancement
- [x] Mettre à jour la liste des rapports
- [x] Créer la page de détails
- [x] Implémenter la résolution de variables
- [x] Ajouter les événements WebSocket
- [x] Tester le flux complet
- [x] Documenter l'implémentation

## 🎉 Résultat

Le système d'exécution de campagnes est maintenant **entièrement fonctionnel** avec:
- ✅ Lancement via modale intuitive
- ✅ Exécution en arrière-plan non bloquante
- ✅ Suivi en temps réel via WebSocket
- ✅ Interface utilisateur réactive
- ✅ Gestion complète des variables
- ✅ Logs détaillés et horodatés
- ✅ Gestion d'erreurs robuste
- ✅ Documentation complète
