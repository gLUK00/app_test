# Développement Frontend

Le frontend est construit en utilisant des technologies web standard, gardées simples pour assurer la maintenabilité.

## Technologies

*   **HTML/Templates** : Jinja2 (Moteur de template Python).
*   **CSS** : Bootstrap 5.3 (copie locale dans `static/vendor`).
*   **JavaScript** : Vanilla JS + un peu de jQuery (héritage).
*   **Icônes** : FontAwesome 6.4 (copie locale).

## Gestion des Assets

Nous n'utilisons pas d'étape de build complexe (Webpack/Vite). Tous les assets sont servis directement depuis le répertoire `static/`.

### Bibliothèques Vendor Locales
Pour respecter la confidentialité et assurer une capacité hors ligne, nous n'utilisons pas de CDN. Toutes les bibliothèques sont stockées dans `static/vendor/`.

## Interactions Dynamiques

### Modales & Formulaires
Nous utilisons les Modales Bootstrap pour les interactions comme "Ajouter une Variable" ou "Uploader un Fichier". JavaScript gère les requêtes AJAX vers l'API.

### Mises à jour Temps Réel
Nous utilisons **Socket.IO** pour mettre à jour l'interface sans recharger.
*   **Exécution de Campagne** : Les barres de progression et les logs se mettent à jour en direct.
*   **Gestion de Fichiers** : La liste des fichiers se met à jour automatiquement lorsqu'un fichier est uploadé/supprimé.

## Ajouter une Nouvelle Page

1.  Créer une route dans `routes/web_routes.py`.
2.  Créer un template dans `templates/` étendant `base.html`.
3.  Ajouter un lien dans la navigation (dans `base.html` ou une vue spécifique).
