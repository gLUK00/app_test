# Gestion des Fichiers dans les Campagnes

## Vue d'ensemble

La gestion des fichiers permet d'uploader, de télécharger et de supprimer des fichiers directement dans le répertoire de travail de chaque campagne. Cette fonctionnalité est essentielle pour :

- Stocker des fichiers de configuration pour les tests
- Conserver des fichiers de données de référence
- Partager des ressources entre les tests d'une même campagne
- Archiver les résultats intermédiaires

## Structure du Répertoire de Travail

Chaque campagne dispose d'un répertoire de travail avec la structure suivante :

```
workdir/
└── {campain_id}/
    ├── files/      # Fichiers gérés via l'interface
    └── work/       # Fichiers temporaires pour l'exécution
```

- **`files/`** : Contient les fichiers uploadés via l'interface utilisateur
- **`work/`** : Utilisé pour les fichiers temporaires générés pendant l'exécution des tests

## Interface Utilisateur

### Section Fichiers

Dans la page de détails d'une campagne (`/campains/{id}`), une section "Fichiers" est disponible entre "Informations" et "Tests de la campagne".

Cette section affiche :
- La liste des fichiers présents dans le répertoire `files/` de la campagne
- Pour chaque fichier :
  - Nom du fichier
  - Taille en Ko (avec 2 décimales)
  - Date de dernière modification
  - Boutons d'action (Télécharger, Supprimer)

### Upload de Fichier

Un bouton "Ajouter un fichier" ouvre une modale permettant de :

1. **Sélectionner un fichier** depuis l'ordinateur
2. **Optionnellement renommer le fichier** avant l'upload
   - Si un nom personnalisé est fourni, le fichier sera enregistré avec ce nom
   - Sinon, le nom original sera conservé
3. **Uploader le fichier** dans le répertoire `files/` de la campagne

**Sécurité** : Les noms de fichiers sont automatiquement sécurisés avec `secure_filename()` pour éviter les injections de chemin.

### Téléchargement de Fichier

Le bouton "Télécharger" permet de récupérer un fichier depuis le serveur. Le fichier est téléchargé avec son nom original.

### Suppression de Fichier

Le bouton "Supprimer" permet de supprimer définitivement un fichier du répertoire de la campagne.

**⚠️ Attention** : La suppression est irréversible. Une confirmation est demandée avant la suppression.

## API REST

### Liste des fichiers

```http
GET /api/campains/{campain_id}/files
Authorization: Bearer {token}
```

**Réponse** (200 OK) :
```json
{
  "files": [
    {
      "name": "config.json",
      "size": 1.52,
      "modified": "2025-10-31T14:30:00"
    }
  ]
}
```

### Upload d'un fichier

```http
POST /api/campains/{campain_id}/files
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: <binary>
customName: "nouveau_nom.txt" (optionnel)
```

**Réponse** (201 Created) :
```json
{
  "message": "Fichier uploadé avec succès",
  "file": {
    "name": "nouveau_nom.txt",
    "size": 2.34,
    "modified": "2025-10-31T14:35:00"
  }
}
```

### Téléchargement d'un fichier

```http
GET /api/campains/{campain_id}/files/{filename}
Authorization: Bearer {token}
```

**Réponse** : Fichier binaire avec en-têtes `Content-Disposition: attachment`

### Suppression d'un fichier

```http
DELETE /api/campains/{campain_id}/files/{filename}
Authorization: Bearer {token}
```

**Réponse** (200 OK) :
```json
{
  "message": "Fichier supprimé avec succès"
}
```

## Rafraîchissement en Temps Réel

La liste des fichiers est automatiquement rafraîchie grâce aux **WebSocket** :

1. Lors de l'ouverture de la page de détails d'une campagne, le client rejoint une "room" WebSocket spécifique à la campagne : `campain_{campain_id}`

2. Lors d'un upload ou d'une suppression de fichier, le serveur émet un événement `files_updated` dans cette room

3. Tous les clients connectés à la page de cette campagne reçoivent l'événement et rafraîchissent automatiquement la liste des fichiers

**Événement WebSocket** :
```javascript
socket.on('files_updated', (data) => {
  if (data.campain_id === campainId) {
    loadFiles(); // Recharger la liste
  }
});
```

## Cas d'Usage

### 1. Fichiers de Configuration

Uploader des fichiers de configuration (JSON, YAML, INI) pour les tests :

```
files/
├── dev_config.json
├── prod_config.json
└── credentials.env
```

### 2. Données de Test

Stocker des fichiers de données pour les tests :

```
files/
├── test_users.csv
├── sample_data.xml
└── reference_image.png
```

### 3. Scripts et Templates

Conserver des scripts ou templates utilisés par les actions :

```
files/
├── script_setup.sh
├── email_template.html
└── report_template.xlsx
```

## Limitations et Bonnes Pratiques

### Limitations

- **Taille maximale** : Dépend de la configuration du serveur web et de Flask
- **Types de fichiers** : Tous les types de fichiers sont acceptés
- **Encodage des noms** : Les noms de fichiers sont sécurisés avec `secure_filename()`

### Bonnes Pratiques

1. **Nommage** :
   - Utilisez des noms de fichiers explicites et sans espaces
   - Préférez les underscores (`_`) aux espaces
   - Incluez l'extension pour identifier le type de fichier

2. **Organisation** :
   - Regroupez les fichiers par fonction (config, data, scripts)
   - Utilisez des préfixes pour catégoriser (ex: `config_`, `data_`)

3. **Sécurité** :
   - Ne stockez jamais de mots de passe en clair dans les fichiers
   - Utilisez le mécanisme de variables pour les données sensibles
   - Vérifiez les permissions d'accès aux fichiers

4. **Maintenance** :
   - Supprimez régulièrement les fichiers obsolètes
   - Documentez le rôle de chaque fichier
   - Vérifiez la taille totale du répertoire `files/`

## Tests

Un script de test complet est disponible : `_build/test_files_management.py`

Ce script teste :
- La création d'une campagne avec le répertoire `files/`
- L'upload de fichiers
- L'upload avec renommage
- Le listing des fichiers
- Le téléchargement de fichiers
- La suppression de fichiers
- Le nettoyage automatique

**Exécution** :
```bash
python3 _build/test_files_management.py
```

## Code Source

### Routes API
- **Fichier** : `routes/campains_routes.py`
- **Fonctions** :
  - `list_files(campain_id)` : Liste les fichiers
  - `upload_file(campain_id)` : Upload un fichier
  - `download_file(campain_id, filename)` : Télécharge un fichier
  - `delete_file(campain_id, filename)` : Supprime un fichier
  - `emit_files_updated(campain_id)` : Émet l'événement WebSocket

### Interface Utilisateur
- **Template** : `templates/campain_details.html`
- **Sections** :
  - Section "Fichiers" avec tableau des fichiers
  - Modale d'upload avec formulaire
  - Code JavaScript pour les opérations CRUD
  - Gestion WebSocket pour le rafraîchissement automatique

### Gestion du Workdir
- **Fichier** : `utils/workdir.py`
- **Fonctions** :
  - `create_campain_workdir(campain_id)` : Crée le répertoire avec `files/` et `work/`
  - `get_campain_workdir(campain_id)` : Récupère le chemin du répertoire
  - `delete_campain_workdir(campain_id)` : Supprime le répertoire complet

## Évolutions Futures

- **Gestion des dossiers** : Permettre de créer des sous-dossiers dans `files/`
- **Versionning** : Conserver l'historique des modifications de fichiers
- **Partage** : Permettre de copier des fichiers entre campagnes
- **Prévisualisation** : Afficher un aperçu des fichiers texte/image
- **Compression** : Télécharger tous les fichiers en archive ZIP
- **Quotas** : Limiter la taille totale des fichiers par campagne
