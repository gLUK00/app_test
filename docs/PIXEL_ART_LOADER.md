# Plugin Pixel Art Loader

## Description

Le plugin **Pixel Art Loader** permet de charger et d'animer des fichiers pixel art au format `.txt` dans une zone `div` spécifiée. Les images défilent avec une animation ligne par ligne et alternent automatiquement selon un intervalle défini.

## Fichiers

- **Plugin JavaScript** : `static/js/pixel-art-loader.js`
- **Fichiers pixel art** : `static/images/art/*.txt`

## Caractéristiques

✅ Chargement de un ou plusieurs fichiers `.txt`  
✅ Première image affichée instantanément  
✅ Transition fluide entre images (remplacement ligne par ligne)  
✅ Animation ligne par ligne avec délai configurable  
✅ Rotation automatique entre plusieurs images  
✅ Adaptation automatique de la taille du conteneur  
✅ API complète pour contrôler l'animation  
✅ Gestion des erreurs robuste  

## Fonctionnement de l'animation

### Première image
Au démarrage, la première image est affichée **instantanément** pour un chargement rapide.

### Images suivantes

#### Mode aléatoire (randomTransition: true) - Par défaut
Les lignes de l'image actuelle sont remplacées dans un **ordre aléatoire** par les lignes de la nouvelle image, créant un effet de "glitch" ou de "dissolution" progressif très dynamique.

#### Mode séquentiel (randomTransition: false)
Les lignes sont remplacées **de haut en bas** de manière ordonnée, créant un effet de "balayage" ou de "morphing" progressif.  

## Installation

### 1. Inclure le script dans votre page HTML

```html
<script src="{{ url_for('static', filename='js/pixel-art-loader.js') }}"></script>
```

### 2. Créer un conteneur dans votre HTML

```html
<div id="pixel-art-mac">
    <pre></pre>
</div>
```

### 3. Initialiser le plugin

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const pixelArtLoader = new PixelArtLoader({
        containerId: 'pixel-art-mac',
        files: ['macgyver1.txt', 'paperclip.txt'],
        interval: 5000,           // Changer d'image toutes les 5 secondes
        lineDelay: 50,            // 50ms entre chaque ligne
        randomTransition: true    // Transition aléatoire (défaut: true)
    });
    
    pixelArtLoader.start();
});
```

## Options de configuration

| Option | Type | Défaut | Description |
|--------|------|--------|-------------|
| `containerId` | String | *requis* | ID du conteneur div |
| `files` | Array | *requis* | Tableau des noms de fichiers `.txt` |
| `interval` | Number | 5000 | Intervalle en ms entre chaque image |
| `lineDelay` | Number | 50 | Délai en ms entre chaque ligne |
| `basePath` | String | '/static/images/art/' | Chemin de base des fichiers |
| `randomTransition` | Boolean | true | Mode de transition : aléatoire (true) ou séquentiel (false) |

## API Publique

### Méthodes

#### `start()`
Démarre l'animation et la rotation des images.

```javascript
pixelArtLoader.start();
```

#### `stop()`
Arrête l'animation et la rotation.

```javascript
pixelArtLoader.stop();
```

#### `next()`
Passe immédiatement à l'image suivante.

```javascript
pixelArtLoader.next();
```

#### `previous()`
Revient à l'image précédente.

```javascript
pixelArtLoader.previous();
```

#### `showArtByIndex(index)`
Affiche une image spécifique par son index.

```javascript
pixelArtLoader.showArtByIndex(0); // Affiche la première image
```

#### `reload()`
Recharge tous les fichiers et redémarre l'animation.

```javascript
await pixelArtLoader.reload();
```

#### `destroy()`
Détruit le plugin et nettoie les ressources.

```javascript
pixelArtLoader.destroy();
```

## Format des fichiers pixel art

Les fichiers doivent être au format `.txt` avec du texte ASCII simple :

```
    ___  ___            _____                       
    |  \/  |           |  __ \                      
    | .  . | __ _  ___ | |  \/_   ___   _____ _ __ 
    | |\/| |/ _` |/ __|| | __ | | | \ \ / / _ \ '__|
    | |  | | (_| | (__ | |_\ \| |_| |\ V /  __/ |   
    \_|  |_/\__,_|\___| \____/ \__, | \_/ \___|_|   
                                __/ |               
                               |___/                
```

## Exemples d'utilisation

### Exemple 1 : Animation simple avec un seul fichier

```javascript
const loader = new PixelArtLoader({
    containerId: 'pixel-art-mac',
    files: ['logo.txt']
});
loader.start();
```

### Exemple 2 : Rotation multiple avec contrôle personnalisé

```javascript
const loader = new PixelArtLoader({
    containerId: 'pixel-art-mac',
    files: ['art1.txt', 'art2.txt', 'art3.txt'],
    interval: 3000,
    lineDelay: 30
});

loader.start();

// Contrôles personnalisés
document.getElementById('btnNext').addEventListener('click', () => {
    loader.next();
});

document.getElementById('btnPrev').addEventListener('click', () => {
    loader.previous();
});

document.getElementById('btnStop').addEventListener('click', () => {
    loader.stop();
});
```

### Exemple 3 : Animation ultra-rapide

```javascript
const loader = new PixelArtLoader({
    containerId: 'pixel-art-mac',
    files: ['animation.txt'],
    lineDelay: 10  // Très rapide
});
loader.start();
```

### Exemple 4 : Transition séquentielle

```javascript
const loader = new PixelArtLoader({
    containerId: 'pixel-art-mac',
    files: ['art1.txt', 'art2.txt', 'art3.txt'],
    interval: 5000,
    lineDelay: 30,
    randomTransition: false  // Mode séquentiel de haut en bas
});
loader.start();
```

## Intégration dans login.html

Le plugin est actuellement utilisé dans `templates/login.html` pour afficher des pixel arts dans la zone de branding à gauche du formulaire de connexion :

```javascript
const pixelArtLoader = new PixelArtLoader({
    containerId: 'pixel-art-mac',
    files: ['macgyver1.txt', 'paperclip.txt'],
    interval: 5000,
    lineDelay: 50
});

pixelArtLoader.start();
```

## CSS Responsive

Le CSS est automatiquement adaptatif grâce aux règles définies dans `static/css/custom.css` :

```css
.pixel-art-mac pre {
    font-family: monospace;
    font-size: clamp(0.15rem, 0.5vw, 0.4rem);
    line-height: 1;
    margin: 0;
    padding: 0;
    color: white;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    white-space: pre;
    overflow: hidden;
}
```

## Gestion des erreurs

Le plugin gère automatiquement les erreurs :

- **Conteneur introuvable** : Lance une exception
- **Fichier manquant** : Affiche une erreur dans la console
- **Paramètres invalides** : Lance une exception avec message explicite

## Performance

- Utilisation de `setTimeout` pour l'animation ligne par ligne (non-bloquant)
- Promesses pour le chargement asynchrone des fichiers
- Nettoyage automatique des timers lors de l'arrêt

## Compatibilité

- ✅ Navigateurs modernes (ES6+)
- ✅ Chrome, Firefox, Safari, Edge
- ✅ Mobile et Desktop
- ✅ Responsive design

## Fichiers d'exemple fournis

1. **macgyver1.txt** : Logo MacGyver en ASCII art
2. **paperclip.txt** : Trombone en ASCII art

## Conseils

- Gardez les fichiers `.txt` légers pour de meilleures performances
- Testez différentes valeurs de `lineDelay` pour l'effet souhaité
- Pour un effet "machine à écrire", utilisez `lineDelay: 100` ou plus
- Pour un affichage instantané, utilisez `lineDelay: 0`

## Dépannage

**Problème** : Les images ne s'affichent pas  
**Solution** : Vérifiez que les fichiers `.txt` existent dans `static/images/art/`

**Problème** : L'animation est trop rapide/lente  
**Solution** : Ajustez `lineDelay` et `interval` selon vos besoins

**Problème** : Le conteneur n'est pas trouvé  
**Solution** : Assurez-vous que le DOM est chargé avant l'initialisation (utilisez `DOMContentLoaded`)

## License

MIT License - Libre d'utilisation dans vos projets TestGyver
