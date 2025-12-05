# Guide Rapide : Autocomplétion des Variables

## 🎯 Qu'est-ce que c'est ?

Un plugin JavaScript qui ajoute automatiquement l'autocomplétion des variables dans tous les champs de saisie de l'application.

## ✨ Fonctionnalités

- 🔍 **Détection automatique** : Surveille votre saisie en temps réel
- 💡 **Suggestions intelligentes** : Propose les variables qui correspondent
- ⌨️ **Navigation clavier** : Utilisez les flèches et Entrée
- 🖱️ **Clic souris** : Cliquez simplement sur une suggestion
- 📱 **Responsive** : Fonctionne sur mobile et tablette
- ⚡ **Performant** : Debouncing et optimisations

## 🚀 Comment l'utiliser ?

### Étape 1 : Commencez à taper
Dans n'importe quel champ `input` ou `textarea`, commencez à taper un mot.

### Étape 2 : Voir les suggestions
Une boîte de suggestions apparaît automatiquement sous le champ.

### Étape 3 : Sélectionner
- **Au clavier** : Flèches ↑↓ puis `Entrée`
- **À la souris** : Cliquez sur la suggestion

### Étape 4 : La variable est insérée
Le mot est remplacé par `{{nom_variable}}` et le curseur est positionné pour continuer.

## 📸 Exemple

```
Vous tapez : "https://api.com/users/use"
↓
Suggestions : username, user_id, user_email
↓
Vous sélectionnez : username
↓
Résultat : "https://api.com/users/{{username}}"
```

## ⌨️ Raccourcis Clavier

| Touche | Action |
|--------|--------|
| `↑` `↓` | Naviguer dans les suggestions |
| `Entrée` | Insérer la variable sélectionnée |
| `Échap` | Fermer les suggestions |

## 🎨 Design

- **Style moderne** : Dégradé violet élégant
- **Animations fluides** : Apparition et transitions smooth
- **Lisibilité** : Mise en évidence des correspondances
- **Icônes** : FontAwesome pour une meilleure UX

## 🔧 Installation

Le plugin est **déjà installé et actif** sur :
- ✅ Page d'ajout de test
- ✅ Page d'édition de test

Aucune configuration requise !

## 📚 Documentation Complète

Pour plus de détails techniques, consultez : [VARIABLE_AUTOCOMPLETE.md](./VARIABLE_AUTOCOMPLETE.md)

## 🐛 En cas de problème

1. Vérifiez que des variables racines existent dans l'admin
2. Ouvrez la console du navigateur (F12)
3. Recherchez les erreurs `[VariableAutocomplete]`
4. Vérifiez votre connexion et votre token

## 💡 Astuces

- Le plugin filtre uniquement les **variables racines** (isRoot=true)
- Les suggestions apparaissent dès **1 caractère** saisi
- Maximum **10 suggestions** affichées à la fois
- Le filtrage est **insensible à la casse**

## 🎯 Cas d'Usage

### Action HTTP
```
URL : https://{{host}}/api/{{endpoint}}
Headers : Authorization: Bearer {{token}}
```

### Action SSH
```
Commande : ssh {{username}}@{{hostname}}
```

### Action FTP
```
Serveur : {{ftp_host}}
Port : {{ftp_port}}
Utilisateur : {{ftp_user}}
```

---

Bon test ! 🚀
