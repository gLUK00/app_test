# Installation Manuelle

Suivez ces étapes pour installer et exécuter TestGyver directement sur votre machine.

## 1. Cloner le Dépôt

```bash
git clone <url-du-depot>
cd app_test
```

## 2. Configurer l'Environnement Virtuel

Il est fortement recommandé d'utiliser un environnement virtuel pour gérer les dépendances.

```bash
# Créer l'environnement virtuel
python3 -m venv .venv

# L'activer
# Sur Linux/macOS :
source .venv/bin/activate
# Sur Windows :
# .venv\Scripts\activate
```

## 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

## 4. Configuration

1.  Copiez la configuration d'exemple (si disponible) ou créez `configuration.json` à la racine.
2.  Voir le [Guide de Configuration](configuration.md) pour les détails des paramètres.

## 5. Initialiser la Base de Données (Optionnel)

Vous pouvez pré-remplir la base de données avec des données initiales et les index.

```bash
python init/init_database.py
```

Pour créer un utilisateur administrateur :
```bash
python init/create_user.py
```

## 6. Lancer l'Application

```bash
# Définir les variables d'environnement
export FLASK_APP=app
export FLASK_ENV=development  # Utilisez 'production' pour le déploiement

# Lancer Flask
flask run --host=0.0.0.0 --port=5000
```

Accédez à l'application sur `http://localhost:5000`.
