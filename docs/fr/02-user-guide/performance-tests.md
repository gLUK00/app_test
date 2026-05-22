# Tests de performance

Les tests de performance vous permettent d'exécuter un ou plusieurs tests existants en les répétant plusieurs fois (instances) et de mesurer les temps de réponse ainsi que les taux de succès.

## Lancer un test de performance

Depuis la page d'une campagne, dans la section **Rapports d'exécution**, cliquez sur le bouton **Test de performance** (en orange, à droite du bouton "Exécuter la campagne").

Vous arrivez alors sur la page de configuration du test de performance.

## Configuration

### Configuration globale

| Champ | Description |
|-------|-------------|
| **Environnement (filière)** | Sélectionnez l'environnement cible (ex. : `dev`, `staging`, `prod`). |
| **Exécuter les tests en parallèle** | Si activé, les différents tests seront lancés simultanément. |
| **Nombre de tests en parallèle** | (Visible si parallèle activé) Nombre maximum de tests s'exécutant en même temps. |

### Configuration par test

Pour chaque test de la campagne, vous pouvez :

| Champ | Description |
|-------|-------------|
| **Inclure** | Cochez/décochez pour inclure ou exclure le test du test de performance. |
| **Nombre d'instances** | Combien de fois le test sera exécuté (ex. : `100` signifie 100 exécutions). |
| **Exécuter les instances en parallèle** | (Visible si instances > 1) Les instances du test s'exécutent en parallèle. |
| **Instances en parallèle** | (Visible si parallèle activé) Nombre maximum d'instances simultanées. |
| **Arrêter sur premier échec d'instance** | (Visible si instances > 1) Stoppe l'exécution dès qu'une instance échoue. |

## Lancement et suivi en temps réel

Cliquez sur **Lancer le test de performance** pour démarrer. Vous êtes automatiquement redirigé vers le **Dashboard de performance** qui affiche :

- Une **barre de progression globale** mise à jour en temps réel (WebSocket)
- Un indicateur **LIVE** rouge animé pendant l'exécution
- Des **statistiques globales** :
  - Instances générées / exécutées / réussies / échouées
  - Temps moyen, minimum, maximum et total d'exécution
- Des **cartes par test** avec les mêmes métriques et une barre de progression individuelle

## Résultats

Une fois le test terminé :
- Le statut final s'affiche (succès ou échecs)
- Le rapport est sauvegardé et visible dans la liste des rapports d'exécution de la campagne avec un badge **PERF** orange
- Cliquer sur le badge ou le rapport ouvre directement le dashboard de performance correspondant

## Rapports de performance dans la liste

Les rapports de performance apparaissent dans la liste des rapports d'exécution avec le badge `PERF` en orange. Le nom du rapport est généré automatiquement sous la forme `Perf - Mois Année` (ex. : `Perf - Juillet 2026`).

## Isolation des variables

Chaque instance d'un test s'exécute dans un contexte de variables isolé. Les variables modifiées par une instance n'affectent pas les autres instances.
