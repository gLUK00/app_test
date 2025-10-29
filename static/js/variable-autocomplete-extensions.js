/**
 * Exemple d'extension du plugin d'autocomplétion
 * Ce fichier montre comment personnaliser et étendre le plugin
 */

// Exemple 1 : Personnalisation basique
// =====================================

// Initialisation avec options personnalisées
const autocomplete = new VariableAutocomplete({
    apiEndpoint: '/api/variables?isRoot=true&page_size=50',
    debounceDelay: 300,      // Attendre 300ms avant de filtrer
    minChars: 2,             // Minimum 2 caractères pour activer
    maxSuggestions: 15       // Afficher jusqu'à 15 suggestions
});


// Exemple 2 : Recharger les variables dynamiquement
// ==================================================

// Après avoir ajouté une nouvelle variable via l'admin
async function refreshVariables() {
    await window.variableAutocomplete.refresh();
    console.log('Variables rechargées !');
}

// Bouton pour rafraîchir
// <button onclick="refreshVariables()">Rafraîchir les variables</button>


// Exemple 3 : Activer/Désactiver le plugin
// =========================================

let autocompleteActive = true;

function toggleAutocomplete() {
    if (autocompleteActive) {
        window.variableAutocomplete.destroy();
        autocompleteActive = false;
        console.log('Autocomplétion désactivée');
    } else {
        window.variableAutocomplete = new VariableAutocomplete();
        autocompleteActive = true;
        console.log('Autocomplétion activée');
    }
}


// Exemple 4 : Écouter les insertions de variables
// ================================================

// Wrapper pour détecter les insertions
document.addEventListener('input', (e) => {
    const field = e.target;
    
    // Vérifier si le champ contient une variable insérée
    if (field.value.includes('{{') && field.value.includes('}}')) {
        console.log('Variable détectée dans le champ:', field.name || field.id);
        
        // Extraire toutes les variables du champ
        const variables = extractVariables(field.value);
        console.log('Variables utilisées:', variables);
    }
});

function extractVariables(text) {
    const regex = /\{\{([^}]+)\}\}/g;
    const matches = [];
    let match;
    
    while ((match = regex.exec(text)) !== null) {
        matches.push(match[1]);
    }
    
    return matches;
}


// Exemple 5 : Validation des variables
// =====================================

async function validateVariables(text) {
    const usedVariables = extractVariables(text);
    const availableVariables = window.variableAutocomplete.variables.map(v => v.key);
    
    const invalid = usedVariables.filter(v => !availableVariables.includes(v));
    
    if (invalid.length > 0) {
        console.warn('Variables invalides détectées:', invalid);
        return false;
    }
    
    console.log('Toutes les variables sont valides');
    return true;
}


// Exemple 6 : Autocomplétion contextuelle
// ========================================

class ContextualAutocomplete extends VariableAutocomplete {
    constructor(options = {}) {
        super(options);
        this.contextMap = {
            'url': ['host', 'port', 'endpoint', 'api_token'],
            'ssh': ['hostname', 'username', 'ssh_key'],
            'ftp': ['ftp_host', 'ftp_user', 'ftp_password'],
            'email': ['email', 'smtp_host', 'smtp_port']
        };
    }
    
    // Override pour filtrer selon le contexte
    showSuggestions(field, currentWord) {
        const context = this.detectContext(field);
        
        if (context) {
            // Filtrer les variables selon le contexte
            const contextVars = this.contextMap[context] || [];
            const originalVars = this.variables;
            
            this.variables = this.variables.filter(v => 
                contextVars.includes(v.key) || v.key.toLowerCase().includes(currentWord.text.toLowerCase())
            );
            
            super.showSuggestions(field, currentWord);
            
            // Restaurer toutes les variables
            this.variables = originalVars;
        } else {
            super.showSuggestions(field, currentWord);
        }
    }
    
    detectContext(field) {
        const label = field.labels?.[0]?.textContent.toLowerCase() || '';
        const name = field.name?.toLowerCase() || '';
        const id = field.id?.toLowerCase() || '';
        
        if (label.includes('url') || name.includes('url')) return 'url';
        if (label.includes('ssh') || name.includes('command')) return 'ssh';
        if (label.includes('ftp') || name.includes('ftp')) return 'ftp';
        if (label.includes('email') || label.includes('mail')) return 'email';
        
        return null;
    }
}


// Exemple 7 : Historique des variables utilisées
// ===============================================

class AutocompleteWithHistory extends VariableAutocomplete {
    constructor(options = {}) {
        super(options);
        this.history = this.loadHistory();
    }
    
    loadHistory() {
        const saved = localStorage.getItem('variable_history');
        return saved ? JSON.parse(saved) : {};
    }
    
    saveHistory() {
        localStorage.setItem('variable_history', JSON.stringify(this.history));
    }
    
    insertVariable(variableKey) {
        super.insertVariable(variableKey);
        
        // Enregistrer dans l'historique
        this.history[variableKey] = (this.history[variableKey] || 0) + 1;
        this.saveHistory();
    }
    
    showSuggestions(field, currentWord) {
        // Trier par fréquence d'utilisation
        const sortedVars = [...this.variables].sort((a, b) => {
            const freqA = this.history[a.key] || 0;
            const freqB = this.history[b.key] || 0;
            return freqB - freqA;
        });
        
        const originalVars = this.variables;
        this.variables = sortedVars;
        
        super.showSuggestions(field, currentWord);
        
        this.variables = originalVars;
    }
}


// Exemple 8 : Prévisualisation des valeurs
// =========================================

class AutocompleteWithPreview extends VariableAutocomplete {
    async showPreview(variableKey) {
        try {
            // Récupérer la valeur de la variable
            const response = await API.get(`/api/variables?key=${variableKey}`);
            const variable = response.items?.[0];
            
            if (variable && variable.value) {
                // Afficher la valeur dans un tooltip
                this.showTooltip(`Valeur : ${variable.value}`);
            }
        } catch (error) {
            console.error('Erreur lors de la récupération de la valeur:', error);
        }
    }
    
    showTooltip(text) {
        // Créer un tooltip simple
        const tooltip = document.createElement('div');
        tooltip.className = 'variable-preview-tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: #333;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            z-index: 10001;
        `;
        
        document.body.appendChild(tooltip);
        
        setTimeout(() => tooltip.remove(), 3000);
    }
}


// Exemple 9 : Export des variables utilisées
// ===========================================

function exportUsedVariables(formId) {
    const form = document.getElementById(formId);
    const fields = form.querySelectorAll('input, textarea');
    const allVariables = new Set();
    
    fields.forEach(field => {
        const variables = extractVariables(field.value);
        variables.forEach(v => allVariables.add(v));
    });
    
    return Array.from(allVariables);
}

function downloadVariablesList(formId) {
    const variables = exportUsedVariables(formId);
    const json = JSON.stringify({ variables }, null, 2);
    
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'variables_used.json';
    a.click();
}


// Exemple 10 : Validation en temps réel
// ======================================

function setupRealTimeValidation() {
    document.addEventListener('input', async (e) => {
        const field = e.target;
        
        if (field.hasAttribute('data-var-autocomplete')) {
            const isValid = await validateVariables(field.value);
            
            if (isValid) {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            } else {
                field.classList.remove('is-valid');
                field.classList.add('is-invalid');
            }
        }
    });
}


// ============================================
// Utilisation des exemples
// ============================================

// Décommenter pour activer l'exemple souhaité :

// 1. Autocomplétion contextuelle
// window.variableAutocomplete = new ContextualAutocomplete();

// 2. Autocomplétion avec historique
// window.variableAutocomplete = new AutocompleteWithHistory();

// 3. Autocomplétion avec prévisualisation
// window.variableAutocomplete = new AutocompleteWithPreview();

// 4. Validation en temps réel
// setupRealTimeValidation();


// ============================================
// Fonctions utilitaires globales
// ============================================

window.VariableUtils = {
    extract: extractVariables,
    validate: validateVariables,
    export: exportUsedVariables,
    download: downloadVariablesList,
    refresh: refreshVariables,
    toggle: toggleAutocomplete
};

console.log('📦 Extensions d\'autocomplétion chargées');
console.log('Utilisez window.VariableUtils pour accéder aux fonctions utilitaires');
