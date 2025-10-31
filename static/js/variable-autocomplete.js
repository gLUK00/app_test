/**
 * Plugin d'autocomplétion pour les variables avec support multi-types
 * Supporte plusieurs types de suggestions avec couleurs et formats d'insertion différents
 */
class VariableAutocomplete {
    constructor(options = {}) {
        this.options = {
            apiEndpoint: options.apiEndpoint || '/api/variables?isRoot=true',
            debounceDelay: options.debounceDelay || 200,
            minChars: options.minChars || 1,
            maxSuggestions: options.maxSuggestions || 10,
            ...options
        };
        
        // Variables par type
        this.variablesByType = {
            testGyver: [],  // Variables TestGyver (variables racines)
            test: [],       // Variables du test en cours
            collection: []  // Variables de collection (test_id, campain_id)
        };
        
        // Configuration des types de suggestions
        this.suggestionTypes = {
            testGyver: {
                color: '#0d6efd',           // Bleu
                bgColor: '#e7f1ff',
                borderColor: '#0d6efd',
                icon: 'fa-database',
                label: 'Variables TestGyver',
                insertFormat: (key) => `{{${key}}}`,  // Format: {{variable_name}}
                displayUppercase: false
            },
            test: {
                color: '#198754',           // Vert
                bgColor: '#d1e7dd',
                borderColor: '#198754',
                icon: 'fa-vial',
                label: 'Variables du test',
                insertFormat: (key) => `{{app.${key}}}`,  // Format: {{app.variable_name}}
                displayUppercase: false
            },
            collection: {
                color: '#dc3545',           // Rouge
                bgColor: '#f8d7da',
                borderColor: '#dc3545',
                icon: 'fa-layer-group',
                label: 'Variables de collection',
                insertFormat: (key) => `{{test.${key}}}`,  // Format: {{test.variable_name}}
                displayUppercase: false
            }
        };
        
        this.activeField = null;
        this.suggestionBox = null;
        this.debounceTimer = null;
        
        this.init();
    }
    
    /**
     * Initialise le plugin
     */
    async init() {
        await this.loadVariables();
        this.initCollectionVariables();
        this.createSuggestionBox();
        this.attachEventListeners();
    }
    
    /**
     * Initialise les variables de collection (disponibles par défaut)
     */
    initCollectionVariables() {
        this.setVariables('collection', [
            { key: 'test_id', description: 'ID du test en cours' },
            { key: 'campain_id', description: 'ID de la campagne' },
            { key: 'files_dir', description: 'Répertoire des fichiers de la campagne' },
            { key: 'work_dir', description: 'Répertoire de travail de la campagne' }
        ]);
    }
    
    /**
     * Définit les variables pour un type spécifique
     * @param {string} type - Type de variables ('testGyver' ou 'test')
     * @param {Array} variables - Tableau de variables (strings ou objets avec propriété 'key')
     */
    setVariables(type, variables) {
        if (!this.suggestionTypes[type]) {
            console.warn(`[VariableAutocomplete] Type inconnu: ${type}`);
            return;
        }
        
        // Normaliser les variables en objets avec au minimum une propriété 'key'
        this.variablesByType[type] = variables.map(v => {
            if (typeof v === 'string') {
                return { key: v };
            }
            return v;
        });
        
        console.log(`[VariableAutocomplete] ${this.variablesByType[type].length} variables ${type} définies`);
    }
    
    /**
     * Charge les variables racines depuis l'API (type testGyver)
     */
    async loadVariables() {
        try {
            console.log('[VariableAutocomplete] Chargement des variables depuis:', this.options.apiEndpoint);
            const response = await API.get(this.options.apiEndpoint);
            
            console.log('[VariableAutocomplete] Réponse API reçue:', response);
            
            // Extraire les variables racines selon le format de la réponse
            let allVariables = [];
            
            if (response.items && Array.isArray(response.items)) {
                allVariables = response.items;
            } else if (response.data && Array.isArray(response.data)) {
                allVariables = response.data;
            } else if (Array.isArray(response)) {
                allVariables = response;
            } else if (response.variables && Array.isArray(response.variables)) {
                allVariables = response.variables;
            } else {
                console.warn('[VariableAutocomplete] Format de réponse non reconnu');
                this.variablesByType.testGyver = [];
                return;
            }
            
            // Filtrer les variables racines
            const rootVariables = allVariables.filter(v => v.isRoot === true);
            this.setVariables('testGyver', rootVariables);
            
            console.log(`[VariableAutocomplete] ${rootVariables.length} variables TestGyver chargées (sur ${allVariables.length} totales)`);
        } catch (error) {
            console.error('[VariableAutocomplete] ❌ Erreur lors du chargement des variables:', error);
            this.variablesByType.testGyver = [];
        }
    }
    
    /**
     * Crée la boîte de suggestions
     */
    createSuggestionBox() {
        this.suggestionBox = document.createElement('div');
        this.suggestionBox.className = 'variable-autocomplete-suggestions';
        this.suggestionBox.style.display = 'none';
        document.body.appendChild(this.suggestionBox);
        
        // Fermer les suggestions en cliquant à l'extérieur
        document.addEventListener('click', (e) => {
            if (e.target !== this.activeField && !this.suggestionBox.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }
    
    /**
     * Attache les événements aux champs
     */
    attachEventListeners() {
        // Observer les mutations du DOM pour gérer les champs ajoutés dynamiquement
        const observer = new MutationObserver(() => {
            this.attachToFields();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Attacher aux champs existants
        this.attachToFields();
    }
    
    /**
     * Attache les événements aux champs input et textarea
     */
    attachToFields() {
        const fields = document.querySelectorAll('input[type="text"]:not([data-var-autocomplete]), textarea:not([data-var-autocomplete])');
        
        if (fields.length > 0) {
            console.log(`[VariableAutocomplete] Attachement de l'autocomplétion à ${fields.length} nouveau(x) champ(s)`);
        }
        
        fields.forEach(field => {
            // Marquer comme traité pour éviter les doublons
            field.setAttribute('data-var-autocomplete', 'true');
            
            field.addEventListener('input', (e) => this.handleInput(e));
            field.addEventListener('keydown', (e) => this.handleKeydown(e));
            field.addEventListener('focus', (e) => this.handleFocus(e));
            
            console.log('[VariableAutocomplete] Champ activé:', field.id || field.name || 'sans id/name', field);
        });
    }
    
    /**
     * Gère l'événement input
     */
    handleInput(e) {
        const field = e.target;
        this.activeField = field;
        
        console.log('[VariableAutocomplete] Input détecté:', field.value, 'dans', field.id || field.name);
        
        // Debounce pour éviter trop de calculs
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.analyzeInput(field);
        }, this.options.debounceDelay);
    }
    
    /**
     * Gère l'événement focus
     */
    handleFocus(e) {
        this.activeField = e.target;
    }
    
    /**
     * Gère les touches clavier
     */
    handleKeydown(e) {
        if (!this.suggestionBox || this.suggestionBox.style.display === 'none') {
            return;
        }
        
        const suggestions = this.suggestionBox.querySelectorAll('.variable-suggestion-tag');
        const selected = this.suggestionBox.querySelector('.variable-suggestion-tag.selected');
        let currentIndex = Array.from(suggestions).indexOf(selected);
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (currentIndex < suggestions.length - 1) {
                    if (selected) selected.classList.remove('selected');
                    suggestions[currentIndex + 1].classList.add('selected');
                    suggestions[currentIndex + 1].scrollIntoView({ block: 'nearest' });
                } else if (suggestions.length > 0) {
                    if (selected) selected.classList.remove('selected');
                    suggestions[0].classList.add('selected');
                    suggestions[0].scrollIntoView({ block: 'nearest' });
                }
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                if (currentIndex > 0) {
                    if (selected) selected.classList.remove('selected');
                    suggestions[currentIndex - 1].classList.add('selected');
                    suggestions[currentIndex - 1].scrollIntoView({ block: 'nearest' });
                } else if (suggestions.length > 0) {
                    if (selected) selected.classList.remove('selected');
                    suggestions[suggestions.length - 1].classList.add('selected');
                    suggestions[suggestions.length - 1].scrollIntoView({ block: 'nearest' });
                }
                break;
                
            case 'Enter':
                if (selected) {
                    e.preventDefault();
                    const variableKey = selected.getAttribute('data-variable-key');
                    const variableType = selected.getAttribute('data-variable-type');
                    this.insertVariable(variableKey, variableType);
                }
                break;
                
            case 'Escape':
                e.preventDefault();
                this.hideSuggestions();
                break;
        }
    }
    
    /**
     * Analyse l'input pour détecter le mot en cours de saisie
     */
    analyzeInput(field) {
        const value = field.value;
        const cursorPos = field.selectionStart;
        
        console.log('[VariableAutocomplete] Analyse:', { value, cursorPos });
        
        // Extraire le mot actuellement en cours de saisie
        const currentWord = this.getCurrentWord(value, cursorPos);
        
        console.log('[VariableAutocomplete] Mot extrait:', currentWord);
        
        if (currentWord.text && currentWord.text.length >= this.options.minChars) {
            console.log('[VariableAutocomplete] Affichage des suggestions pour:', currentWord.text);
            this.showSuggestions(field, currentWord);
        } else {
            console.log('[VariableAutocomplete] Mot trop court ou vide, masquage des suggestions');
            this.hideSuggestions();
        }
    }
    
    /**
     * Extrait le mot en cours de saisie à la position du curseur
     */
    getCurrentWord(text, cursorPos) {
        // Chercher le début du mot (caractères alphanumériques et underscore)
        let start = cursorPos;
        while (start > 0 && /[a-zA-Z0-9_]/.test(text[start - 1])) {
            start--;
        }
        
        // Chercher la fin du mot
        let end = cursorPos;
        while (end < text.length && /[a-zA-Z0-9_]/.test(text[end])) {
            end++;
        }
        
        return {
            text: text.substring(start, end),
            start: start,
            end: end
        };
    }
    
    /**
     * Affiche les suggestions filtrées
     */
    showSuggestions(field, currentWord) {
        const word = currentWord.text.toLowerCase();
        
        // Collecter les suggestions de tous les types
        const suggestionsByType = {};
        let totalSuggestions = 0;
        
        for (const [type, config] of Object.entries(this.suggestionTypes)) {
            const variables = this.variablesByType[type] || [];
            const filtered = variables.filter(v => 
                v.key.toLowerCase().includes(word)
            ).slice(0, this.options.maxSuggestions);
            
            if (filtered.length > 0) {
                suggestionsByType[type] = {
                    config: config,
                    variables: filtered
                };
                totalSuggestions += filtered.length;
            }
        }
        
        if (totalSuggestions === 0) {
            this.hideSuggestions();
            return;
        }
        
        // Créer le HTML des suggestions groupées par type
        let html = '<div class="variable-suggestions-container">';
        
        let globalIndex = 0;
        for (const [type, data] of Object.entries(suggestionsByType)) {
            html += `
                <div class="variable-suggestions-group" data-type="${type}">
                    <div class="variable-suggestions-header" style="border-left: 3px solid ${data.config.borderColor}; background-color: ${data.config.bgColor};">
                        <i class="fas ${data.config.icon}" style="color: ${data.config.color};"></i>
                        <span style="color: ${data.config.color};">${data.config.label}</span>
                    </div>
                    <div class="variable-suggestions-list">
                        ${data.variables.map((v, index) => {
                            const displayKey = data.config.displayUppercase ? v.key.toUpperCase() : v.key;
                            const isFirst = globalIndex === 0;
                            globalIndex++;
                            
                            return `
                                <div class="variable-suggestion-tag ${isFirst ? 'selected' : ''}" 
                                     data-variable-key="${v.key}"
                                     data-variable-type="${type}"
                                     style="border-left: 3px solid ${data.config.borderColor};"
                                     title="${v.description || v.key}">
                                    <i class="fas fa-code" style="color: ${data.config.color};"></i>
                                    <span class="variable-key" style="color: ${data.config.color};">${this.highlightMatch(displayKey, word)}</span>
                                    ${v.description ? `<span class="variable-desc">${v.description}</span>` : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        this.suggestionBox.innerHTML = html;
        
        // Positionner la boîte de suggestions
        this.positionSuggestionBox(field);
        
        // Attacher les événements de clic
        const tags = this.suggestionBox.querySelectorAll('.variable-suggestion-tag');
        tags.forEach(tag => {
            tag.addEventListener('click', () => {
                const variableKey = tag.getAttribute('data-variable-key');
                const variableType = tag.getAttribute('data-variable-type');
                this.insertVariable(variableKey, variableType);
            });
            
            tag.addEventListener('mouseenter', () => {
                tags.forEach(t => t.classList.remove('selected'));
                tag.classList.add('selected');
            });
        });
        
        this.suggestionBox.style.display = 'block';
    }
    
    /**
     * Met en évidence la correspondance dans le texte
     */
    highlightMatch(text, match) {
        const index = text.toLowerCase().indexOf(match);
        if (index === -1) return text;
        
        return text.substring(0, index) + 
               '<strong>' + text.substring(index, index + match.length) + '</strong>' + 
               text.substring(index + match.length);
    }
    
    /**
     * Positionne la boîte de suggestions sous le champ
     */
    positionSuggestionBox(field) {
        const rect = field.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        
        this.suggestionBox.style.position = 'absolute';
        this.suggestionBox.style.top = (rect.bottom + scrollTop + 5) + 'px';
        this.suggestionBox.style.left = (rect.left + scrollLeft) + 'px';
        this.suggestionBox.style.width = Math.max(rect.width, 300) + 'px';
    }
    
    /**
     * Cache les suggestions
     */
    hideSuggestions() {
        if (this.suggestionBox) {
            this.suggestionBox.style.display = 'none';
        }
    }
    
    /**
     * Insère la variable sélectionnée dans le champ
     */
    insertVariable(variableKey, variableType = 'testGyver') {
        if (!this.activeField) return;
        
        const field = this.activeField;
        const value = field.value;
        const cursorPos = field.selectionStart;
        
        // Obtenir le mot actuel pour le remplacer
        const currentWord = this.getCurrentWord(value, cursorPos);
        
        // Obtenir le format d'insertion selon le type
        const typeConfig = this.suggestionTypes[variableType];
        const variableText = typeConfig ? typeConfig.insertFormat(variableKey) : `{{${variableKey}}}`;
        
        // Construire la nouvelle valeur avec la variable insérée
        const before = value.substring(0, currentWord.start);
        const after = value.substring(currentWord.end);
        
        field.value = before + variableText + after;
        
        // Positionner le curseur à la fin de la variable insérée
        const newCursorPos = currentWord.start + variableText.length;
        field.setSelectionRange(newCursorPos, newCursorPos);
        field.focus();
        
        // Déclencher l'événement input pour les éventuels listeners
        field.dispatchEvent(new Event('input', { bubbles: true }));
        
        this.hideSuggestions();
    }
    
    /**
     * Recharge les variables (utile si elles changent)
     */
    async refresh() {
        await this.loadVariables();
    }
    
    /**
     * Détruit le plugin
     */
    destroy() {
        if (this.suggestionBox) {
            this.suggestionBox.remove();
        }
        
        // Retirer les attributs des champs
        const fields = document.querySelectorAll('[data-var-autocomplete]');
        fields.forEach(field => {
            field.removeAttribute('data-var-autocomplete');
        });
    }
}

// Export pour utilisation globale
window.VariableAutocomplete = VariableAutocomplete;
