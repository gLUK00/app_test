# Structure du Projet

```text
/
├── app.py                  # Point d'entrée de l'application
├── configuration.json      # Fichier de configuration principal
├── Dockerfile              # Définition du conteneur
├── requirements.txt        # Dépendances Python
├── docs/                   # Documentation (Vous êtes ici)
├── init/                   # Scripts d'initialisation (BDD, Utilisateurs)
├── models/                 # Modèles de base de données (User, Campain, Test...)
├── plugins/                # Système de plugins
│   ├── actions/            # Implémentation des plugins d'action
│   ├── plugin_base.py      # Classe de base pour tous les plugins
│   └── plugin_manager.py   # Logique de découverte des plugins
├── routes/                 # Routes API et Web (Blueprints)
├── static/                 # Assets statiques (CSS, JS, Images, Libs Vendor)
├── templates/              # Templates HTML Jinja2
├── translations/           # Fichiers de traduction i18n
├── utils/                  # Modules utilitaires (BDD, Auth, Exécution...)
└── workdir/                # Stockage d'exécution pour les campagnes
```

## Répertoires Clés

*   **`models/`** : Contient les classes Python représentant les documents MongoDB. Elles gèrent les opérations CRUD.
*   **`routes/`** : Sépare la logique de l'application en modules (Auth, API, Web UI).
*   **`plugins/actions/`** : C'est ici que vous ajoutez de nouvelles capacités au système.
*   **`utils/`** : Contient la logique centrale pour les tâches complexes comme `campain_executor.py` (le lanceur de tests).
