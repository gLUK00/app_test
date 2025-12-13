/**
 * Plugin Pixel Art Loader
 * Charge et anime des fichiers pixel art (.txt) dans une zone div spécifiée
 * 
 * Utilisation :
 * const loader = new PixelArtLoader({
 *     containerId: 'pixel-art-mac',
 *     files: ['art1.txt', 'art2.txt'],
 *     interval: 8080,        // Intervalle entre les images en ms (défaut: 8080)
 *     lineDelay: 50,         // Délai entre chaque ligne en ms (défaut: 50)
 *     randomTransition: true // Transition aléatoire ou séquentielle (défaut: true)
 * });
 * loader.start();
 */

class PixelArtLoader {
    constructor(options = {}) {
        // Validation des paramètres
        if (!options.containerId) {
            throw new Error('PixelArtLoader: containerId est requis');
        }
        
        if (!options.files || !Array.isArray(options.files) || options.files.length === 0) {
            throw new Error('PixelArtLoader: files doit être un tableau non vide');
        }

        // Configuration
        this.containerId = options.containerId;
        this.files = options.files;
        this.interval = options.interval || 8080; // 5 secondes par défaut
        this.lineDelay = options.lineDelay || 50; // 50ms entre chaque ligne
        this.basePath = options.basePath || '/static/images/art/';
        this.randomTransition = options.randomTransition !== undefined ? options.randomTransition : true; // Aléatoire par défaut
        
        // État interne
        this.container = null;
        this.preElement = null;
        this.artContents = [];
        this.currentIndex = -1; // Commence à -1 pour que la première image soit à l'index 0
        this.isAnimating = false;
        this.intervalId = null;
        this.animationTimeout = null;
        this.isReady = false;
        this.isFirstLoad = true; // Flag pour la première image
        
        // Initialisation (async)
        this.initPromise = this.init();
    }

    /**
     * Initialise le plugin
     */
    async init() {
        try {
            // Récupérer le conteneur
            this.container = document.getElementById(this.containerId);
            if (!this.container) {
                throw new Error(`PixelArtLoader: Conteneur avec l'id "${this.containerId}" introuvable`);
            }

            // Récupérer ou créer l'élément <pre>
            this.preElement = this.container.querySelector('pre');
            if (!this.preElement) {
                this.preElement = document.createElement('pre');
                this.container.appendChild(this.preElement);
            }

            // Charger tous les fichiers
            await this.loadAllFiles();
            this.isReady = true;
            console.log('PixelArtLoader: Prêt');
        } catch (error) {
            console.error('PixelArtLoader: Erreur lors de l\'initialisation', error);
            throw error;
        }
    }

    /**
     * Charge tous les fichiers pixel art
     */
    async loadAllFiles() {
        try {
            const promises = this.files.map(file => this.loadFile(file));
            this.artContents = await Promise.all(promises);
            console.log(`PixelArtLoader: ${this.artContents.length} fichier(s) chargé(s)`);
        } catch (error) {
            console.error('PixelArtLoader: Erreur lors du chargement des fichiers', error);
            throw error;
        }
    }

    /**
     * Charge un fichier pixel art
     */
    async loadFile(filename) {
        const url = `${this.basePath}${filename}`;
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const content = await response.text();
            return {
                filename: filename,
                content: content,
                lines: content.split('\n')
            };
        } catch (error) {
            console.error(`PixelArtLoader: Erreur lors du chargement de ${filename}`, error);
            throw error;
        }
    }

    /**
     * Démarre l'animation
     */
    async start() {
        // Attendre que l'initialisation soit terminée
        await this.initPromise;
        
        if (!this.isReady) {
            console.error('PixelArtLoader: Le plugin n\'est pas prêt');
            return;
        }
        
        if (this.artContents.length === 0) {
            console.error('PixelArtLoader: Aucun contenu à afficher');
            return;
        }

        // Afficher le premier art
        this.showNextArt();
        this.showNextArt();

        // Si plusieurs fichiers, démarrer la rotation
        if (this.artContents.length > 1) {
            this.intervalId = setInterval(() => {
                if (!this.isAnimating) {
                    this.showNextArt();
                }
            }, this.interval);
        }
    }

    /**
     * Arrête l'animation
     */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        if (this.animationTimeout) {
            clearTimeout(this.animationTimeout);
            this.animationTimeout = null;
        }
        this.isAnimating = false;
    }

    /**
     * Affiche le pixel art suivant avec animation ligne par ligne
     */
    async showNextArt() {
        if (this.isAnimating) {
            return;
        }

        this.isAnimating = true;
        const nextIndex = (this.currentIndex + 1) % this.artContents.length;
        const nextArt = this.artContents[nextIndex];
        
        // Si c'est la première image, charger instantanément
        if (this.isFirstLoad) {
            this.preElement.textContent = nextArt.lines.join('\n');
            this.isFirstLoad = false;
        } else {
            // Transition ligne par ligne de l'image actuelle vers la suivante
            await this.transitionToNextArt(nextArt.lines);
        }
        
        // Passer à l'index suivant
        this.currentIndex = nextIndex;
        this.isAnimating = false;
    }

    /**
     * Transition ligne par ligne entre deux images
     */
    transitionToNextArt(newLines) {
        return new Promise((resolve) => {
            const currentLines = this.preElement.textContent.split('\n');
            const maxLines = Math.max(currentLines.length, newLines.length);
            
            if (this.randomTransition) {
                // Mode aléatoire : remplacer les lignes dans un ordre aléatoire
                this.randomTransition_internal(currentLines, newLines, maxLines, resolve);
            } else {
                // Mode séquentiel : remplacer les lignes de haut en bas
                this.sequentialTransition(currentLines, newLines, maxLines, resolve);
            }
        });
    }

    /**
     * Transition séquentielle (de haut en bas)
     */
    sequentialTransition(currentLines, newLines, maxLines, resolve) {
        let currentLine = 0;

        const replaceNextLine = () => {
            if (currentLine < maxLines) {
                // Créer le tableau des lignes en cours de transition
                const transitionLines = [];
                
                // Ajouter les nouvelles lignes déjà remplacées
                for (let i = 0; i < currentLine; i++) {
                    transitionLines.push(newLines[i] || '');
                }
                
                // Ajouter les anciennes lignes restantes
                for (let i = currentLine; i < currentLines.length; i++) {
                    transitionLines.push(currentLines[i] || '');
                }
                
                // Afficher le résultat
                this.preElement.textContent = transitionLines.join('\n');
                currentLine++;
                
                this.animationTimeout = setTimeout(replaceNextLine, this.lineDelay);
            } else {
                // À la fin, afficher complètement la nouvelle image
                this.preElement.textContent = newLines.join('\n');
                resolve();
            }
        };

        replaceNextLine();
    }

    /**
     * Transition aléatoire
     */
    randomTransition_internal(currentLines, newLines, maxLines, resolve) {
        // Créer un tableau d'indices à remplacer
        const indices = Array.from({ length: maxLines }, (_, i) => i);
        
        // Mélanger aléatoirement les indices (algorithme de Fisher-Yates)
        for (let i = indices.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [indices[i], indices[j]] = [indices[j], indices[i]];
        }
        
        // Copier les lignes actuelles
        const transitionLines = [...currentLines];
        // S'assurer que le tableau a la bonne taille
        while (transitionLines.length < maxLines) {
            transitionLines.push('');
        }
        
        let replacedCount = 0;

        const replaceNextLine = () => {
            if (replacedCount < maxLines) {
                // Remplacer la ligne à l'indice aléatoire
                const lineIndex = indices[replacedCount];
                transitionLines[lineIndex] = newLines[lineIndex] || '';
                
                // Afficher le résultat
                this.preElement.textContent = transitionLines.join('\n');
                replacedCount++;
                
                this.animationTimeout = setTimeout(replaceNextLine, this.lineDelay);
            } else {
                // À la fin, afficher complètement la nouvelle image
                this.preElement.textContent = newLines.join('\n');
                resolve();
            }
        };

        replaceNextLine();
    }

    /**
     * Passe au pixel art suivant immédiatement
     */
    async next() {
        await this.initPromise;
        if (!this.isAnimating && this.isReady) {
            this.showNextArt();
        }
    }

    /**
     * Passe au pixel art précédent
     */
    async previous() {
        await this.initPromise;
        if (!this.isAnimating && this.isReady) {
            this.currentIndex = (this.currentIndex - 2 + this.artContents.length) % this.artContents.length;
            this.showNextArt();
        }
    }

    /**
     * Affiche un pixel art spécifique par son index
     */
    async showArtByIndex(index) {
        await this.initPromise;
        if (index >= 0 && index < this.artContents.length && !this.isAnimating && this.isReady) {
            this.currentIndex = index;
            this.showNextArt();
        }
    }

    /**
     * Recharge tous les fichiers
     */
    async reload() {
        this.stop();
        await this.loadAllFiles();
        this.currentIndex = -1;
        this.isFirstLoad = true; // Réinitialiser le flag
        this.start();
    }

    /**
     * Détruit le plugin et nettoie les ressources
     */
    destroy() {
        this.stop();
        if (this.preElement) {
            this.preElement.textContent = '';
        }
        this.artContents = [];
        this.currentIndex = -1;
        this.isFirstLoad = true;
    }
}

// Export pour utilisation en module ou global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PixelArtLoader;
}
