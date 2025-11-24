# Script de Création d'Utilisateur

## Description

Le script `create_user.py` permet de créer facilement des utilisateurs dans TestGyver. Il supporte deux modes d'utilisation : **interactif** et **ligne de commande**.

## Prérequis

- Python 3.x installé
- MongoDB en cours d'exécution
- Configuration correcte dans `configuration.json`

## Utilisation

### Mode Interactif (Recommandé)

Le mode interactif guide l'utilisateur pas à pas avec des prompts clairs :

```bash
python3 init/create_user.py
```

Le script demandera :
1. **Nom** de l'utilisateur
2. **Email** (avec validation du format)
3. **Mot de passe** (minimum 8 caractères, saisi en mode masqué)
4. **Confirmation** du mot de passe
5. **Rôle** (admin ou user)

### Mode Ligne de Commande

Pour une utilisation en script ou automatisation :

```bash
python3 init/create_user.py -n "John Doe" -e john@example.com -p MyPassword123 -r admin
```

**Options disponibles :**

- `-n, --name` : Nom de l'utilisateur (requis)
- `-e, --email` : Email de l'utilisateur (requis)
- `-p, --password` : Mot de passe (requis, min. 8 caractères)
- `-r, --role` : Rôle (admin ou user) (requis)

**Exemples :**

```bash
# Créer un administrateur
python3 init/create_user.py -n "Admin User" -e admin@testgyver.com -p SecurePass123 -r admin

# Créer un utilisateur standard
python3 init/create_user.py --name "Jane Doe" --email jane@example.com --password MySecret456 --role user
```

## Validation

Le script effectue les validations suivantes :

### Email
- Format valide (ex: `user@domain.com`)
- Unicité (pas de doublon dans la base)

### Mot de passe
- Minimum 8 caractères
- Confirmation en mode interactif

### Rôle
- Doit être `admin` ou `user`

## Codes de Sortie

- `0` : Succès
- `1` : Erreur (connexion MongoDB, validation, utilisateur existant, etc.)

## Messages

Le script utilise des couleurs pour une meilleure lisibilité :

- 🟢 **Vert** : Succès
- 🔵 **Bleu** : En-têtes
- 🟡 **Jaune** : Avertissements
- 🔴 **Rouge** : Erreurs
- 🔷 **Cyan** : Informations

## Gestion des Erreurs

### Utilisateur déjà existant

```
✗ Un utilisateur avec l'email 'john@example.com' existe déjà
```

**Solution :** Utilisez un email différent ou supprimez l'utilisateur existant.

### Connexion MongoDB échouée

```
✗ Impossible de se connecter à MongoDB: ...
```

**Solutions :**
- Vérifier que MongoDB est démarré
- Vérifier les credentials dans `configuration.json`
- Vérifier l'hôte et le port MongoDB

### Format email invalide

```
✗ Format d'email invalide
```

**Solution :** Utilisez un email au format `user@domain.com`

### Mot de passe trop court

```
✗ Le mot de passe doit contenir au moins 8 caractères
```

**Solution :** Utilisez un mot de passe d'au moins 8 caractères

## Annulation

En mode interactif, vous pouvez annuler l'opération avec `Ctrl+C` :

```
⚠ Opération annulée par l'utilisateur
```

## Sécurité

- Le mot de passe est saisi en mode masqué (non visible à l'écran) en mode interactif
- Le mot de passe est hashé avec bcrypt avant stockage en base
- En ligne de commande, évitez de stocker le mot de passe dans l'historique bash :
  ```bash
  # Ajouter un espace avant la commande pour éviter l'historique (selon config bash)
   python3 init/create_user.py -n "..." -e "..." -p "..." -r admin
  ```

## Rôles

### Admin
- Accès à toutes les fonctionnalités
- Gestion des utilisateurs
- Gestion des variables globales

### User
- Accès aux campagnes et tests
- Création et modification de ses propres tests
- Pas d'accès aux fonctionnalités d'administration

## Exemples Complets

### Création du premier administrateur

```bash
$ python3 init/create_user.py

============================================================
          CRÉATION D'UTILISATEUR - MODE INTERACTIF
============================================================

ℹ Chargement de la configuration...
✓ Connexion à MongoDB établie
Nom de l'utilisateur: John Admin
Email: admin@testgyver.com
Mot de passe (min. 8 caractères): ********
Confirmez le mot de passe: ********

Rôle de l'utilisateur:
  1. admin (administrateur)
  2. user (utilisateur standard)
Choix (1 ou 2): 1

ℹ Création de l'utilisateur 'John Admin'...
✓ Utilisateur créé avec succès!
ℹ   ID: 507f1f77bcf86cd799439011
ℹ   Nom: John Admin
ℹ   Email: admin@testgyver.com
ℹ   Rôle: admin

✓ Opération terminée avec succès!
```

### Création en batch (script)

```bash
#!/bin/bash
# Script de création d'utilisateurs en masse

python3 init/create_user.py -n "Admin" -e admin@company.com -p Admin123456 -r admin
python3 init/create_user.py -n "Test User 1" -e user1@company.com -p User123456 -r user
python3 init/create_user.py -n "Test User 2" -e user2@company.com -p User123456 -r user
```

## Aide

Pour afficher l'aide :

```bash
python3 init/create_user.py --help
```
