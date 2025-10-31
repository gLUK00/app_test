# Migration des CDN vers des fichiers locaux

## 📋 Vue d'ensemble

Ce document décrit la migration de tous les CDN externes vers des fichiers locaux hébergés dans le répertoire `static/vendor/`.

## 🎯 Objectifs

- ✅ Améliorer les performances de chargement
- ✅ Réduire la dépendance aux services tiers
- ✅ Permettre le fonctionnement hors ligne
- ✅ Améliorer la sécurité (pas de ressources externes)
- ✅ Respecter les politiques de confidentialité (RGPD)

## 📦 Bibliothèques migrées

### 1. Bootstrap 5.3.0
- **CDN d'origine** : `https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/`
- **Emplacement local** : `static/vendor/bootstrap/`
- **Fichiers** :
  - `css/bootstrap.min.css` (228 KB)
  - `js/bootstrap.bundle.min.js` (79 KB)

### 2. Font Awesome 6.4.0
- **CDN d'origine** : `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/`
- **Emplacement local** : `static/vendor/fontawesome/`
- **Fichiers** :
  - `css/all.min.css` (100 KB)
  - `webfonts/fa-solid-900.woff2` (147 KB)
  - `webfonts/fa-regular-400.woff2` (25 KB)
  - `webfonts/fa-brands-400.woff2` (106 KB)

### 3. Socket.IO 4.5.4
- **CDN d'origine** : `https://cdn.socket.io/4.5.4/`
- **Emplacement local** : `static/vendor/socket.io/`
- **Fichiers** :
  - `socket.io.min.js` (44 KB)

## 📂 Structure des fichiers

```
static/
└── vendor/
    ├── bootstrap/
    │   ├── css/
    │   │   └── bootstrap.min.css
    │   └── js/
    │       └── bootstrap.bundle.min.js
    ├── fontawesome/
    │   ├── css/
    │   │   └── all.min.css
    │   └── webfonts/
    │       ├── fa-solid-900.woff2
    │       ├── fa-regular-400.woff2
    │       └── fa-brands-400.woff2
    └── socket.io/
        └── socket.io.min.js
```

## 🔧 Fichiers modifiés

### Templates
1. **templates/base.html**
   - Bootstrap CSS : CDN → local
   - Bootstrap JS : CDN → local
   - Font Awesome CSS : CDN → local

2. **templates/login.html**
   - Bootstrap CSS : CDN → local
   - Bootstrap JS : CDN → local
   - Font Awesome CSS : CDN → local

3. **templates/rapport_details.html**
   - Socket.IO JS : CDN → local

### Fichiers de test statiques
4. **static/test-autocomplete.html**
   - Bootstrap CSS : CDN → local
   - Font Awesome CSS : CDN → local

5. **static/test-multitype-autocomplete.html**
   - Bootstrap CSS : CDN → local
   - Font Awesome CSS : CDN → local

## 🔍 Modifications techniques

### Correction des chemins Font Awesome
Les chemins des polices dans le fichier `all.min.css` ont été corrigés :
```bash
sed -i 's|../webfonts/|../../fontawesome/webfonts/|g' all.min.css
```

### Exemple de changement
**Avant :**
```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
```

**Après :**
```html
<link href="{{ url_for('static', filename='vendor/bootstrap/css/bootstrap.min.css') }}" rel="stylesheet">
```

## ✅ Vérification

Pour vérifier qu'aucun CDN n'est utilisé :
```bash
grep -r "https://cdn\|https://cdnjs\|https://jsdelivr" templates/ static/
```

## 💾 Taille totale

- **Taille totale des fichiers vendor** : ~729 KB
- **Gain en requêtes HTTP externes** : 7 requêtes éliminées

## 📝 Maintenance

### Mise à jour des bibliothèques

Pour mettre à jour une bibliothèque, téléchargez la nouvelle version et remplacez les fichiers :

**Bootstrap :**
```bash
cd static/vendor/bootstrap/css
curl -sL -o bootstrap.min.css https://cdn.jsdelivr.net/npm/bootstrap@VERSION/dist/css/bootstrap.min.css

cd ../js
curl -sL -o bootstrap.bundle.min.js https://cdn.jsdelivr.net/npm/bootstrap@VERSION/dist/js/bootstrap.bundle.min.js
```

**Font Awesome :**
```bash
cd static/vendor/fontawesome/css
curl -sL -o all.min.css https://cdnjs.cloudflare.com/ajax/libs/font-awesome/VERSION/css/all.min.css
sed -i 's|../webfonts/|../../fontawesome/webfonts/|g' all.min.css

cd ../webfonts
curl -sL -o fa-solid-900.woff2 https://cdnjs.cloudflare.com/ajax/libs/font-awesome/VERSION/webfonts/fa-solid-900.woff2
curl -sL -o fa-regular-400.woff2 https://cdnjs.cloudflare.com/ajax/libs/font-awesome/VERSION/webfonts/fa-regular-400.woff2
curl -sL -o fa-brands-400.woff2 https://cdnjs.cloudflare.com/ajax/libs/font-awesome/VERSION/webfonts/fa-brands-400.woff2
```

**Socket.IO :**
```bash
cd static/vendor/socket.io
curl -sL -o socket.io.min.js https://cdn.socket.io/VERSION/socket.io.min.js
```

## 🎉 Avantages de la migration

1. **Performance** : Pas de latence réseau vers des CDN externes
2. **Fiabilité** : Aucune dépendance à la disponibilité des CDN
3. **Sécurité** : Contrôle total sur les fichiers servis
4. **Confidentialité** : Pas de tracking tiers
5. **Hors ligne** : Fonctionnement sans connexion Internet
6. **Cache** : Meilleur contrôle du cache navigateur

## 📅 Date de migration

Migration effectuée le : **31 octobre 2025**
