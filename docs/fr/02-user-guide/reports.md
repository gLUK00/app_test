# Rapports et Suivi

Les rapports fournissent un historique détaillé des exécutions de campagne.

## Accéder aux Rapports

*   **Depuis le Tableau de Bord** : L'onglet "Rapports" (si disponible) ou via la page Détails de la Campagne.
*   **Depuis la Campagne** : La section "Rapports" liste toutes les exécutions pour cette campagne.

## Détails du Rapport

Cliquer sur un rapport ouvre la vue détaillée :

![Détails du rapport](../../assets/campaign_rapport.png)
> Page de détails d'un rapport montrant l'en-tête de statut et la liste des tests exécutés avec leurs icônes.

### En-tête
*   **Statut** : Succès, Échec, ou En cours.
*   **Progression** : Pourcentage de complétion.
*   **Environnement** : L'environnement utilisé pour l'exécution.
*   **Temps** : Heure de début, Heure de fin, et Durée totale.

### Résultats des Tests
Une liste de tous les tests exécutés dans la campagne.
*   **Icône de Statut** : ✅ Réussi / ❌ Échoué.
*   **Logs** : Cliquez pour développer les logs d'exécution détaillés.
    *   Voir exactement quelles données ont été envoyées et reçues.
    *   Voir le temps d'exécution pour chaque action.
    *   Voir les messages d'erreur si une action a échoué.

## Mises à jour Temps Réel
Les rapports utilisent les WebSockets pour se mettre à jour en temps réel. Vous n'avez pas besoin de rafraîchir la page pour voir la progression d'une campagne en cours.

## Génération de Rapports

Vous pouvez générer des rapports exportables (PDF, HTML, etc.) à partir des résultats d'exécution.

1.  Dans la section **Informations générales**, cliquez sur le bouton **Generate report**.
2.  Une fenêtre modale s'ouvre. Sélectionnez le **Type de rapport** souhaité (par exemple, HTML, PDF).
3.  Remplissez les champs de configuration spécifiques au rapport choisi (titre, options d'affichage, etc.).
4.  Cliquez sur **Générer**.
5.  Une fois le rapport généré, un lien de téléchargement apparaîtra.
