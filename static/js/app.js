/* Fonctions JavaScript communes pour TestGyver */

// Gestion du token JWT
const Auth = {
    getToken() {
        return localStorage.getItem('token');
    },
    
    setToken(token) {
        localStorage.setItem('token', token);
    },
    
    removeToken() {
        localStorage.removeItem('token');
    },
    
    getHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
    }
};

// Requêtes API
const API = {
    async request(url, options = {}) {
        const defaultOptions = {
            headers: Auth.getHeaders()
        };
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (response.status === 401) {
            const data = await response.json().catch(() => ({}));
            const message = data.message || 'Votre session a expiré. Veuillez vous reconnecter.';
            
            // Afficher un message avant la redirection
            if (typeof Notification !== 'undefined') {
                Notification.error(message);
            } else {
                alert(message);
            }
            
            Auth.removeToken();
            
            // Redirection après un court délai pour permettre la lecture du message
            setTimeout(() => {
                window.location.href = '/?error=session_expired';
            }, 1500);
            
            throw new Error(message);
        }
        
        const data = await response.json();
        
        // Si la réponse n'est pas OK (status code n'est pas 2xx), lancer une erreur
        if (!response.ok) {
            throw new Error(data.message || `Erreur HTTP: ${response.status}`);
        }
        
        return data;
    },
    
    async get(url) {
        return this.request(url, { method: 'GET' });
    },
    
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
};

// Affichage des notifications
const Notification = {
    show(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    },
    
    success(message) {
        this.show(message, 'success');
    },
    
    error(message) {
        this.show(message, 'danger');
    },
    
    warning(message) {
        this.show(message, 'warning');
    },
    
    info(message) {
        this.show(message, 'info');
    }
};

// Gestion des variables (autocomplete)
const VariableHelper = {
    variables: [],
    
    async loadVariables() {
        try {
            const data = await API.get('/api/variables');
            this.variables = data.data || [];
        } catch (error) {
            console.error('Erreur lors du chargement des variables:', error);
        }
    },
    
    setupAutocomplete(inputElement) {
        if (!inputElement) return;
        
        inputElement.addEventListener('input', (e) => {
            const value = e.target.value;
            const cursorPos = e.target.selectionStart;
            const textBeforeCursor = value.substring(0, cursorPos);
            
            // Chercher le début d'un tag {{
            const lastBraceIndex = textBeforeCursor.lastIndexOf('{{');
            
            if (lastBraceIndex !== -1) {
                const searchTerm = textBeforeCursor.substring(lastBraceIndex + 2);
                
                if (searchTerm && !searchTerm.includes('}}')) {
                    this.showSuggestions(inputElement, searchTerm, lastBraceIndex);
                    return;
                }
            }
            
            this.hideSuggestions();
        });
    },
    
    showSuggestions(inputElement, searchTerm, insertPos) {
        const suggestions = this.variables.filter(v => 
            v.key.toLowerCase().includes(searchTerm.toLowerCase())
        );
        
        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }
        
        let suggestionBox = document.getElementById('variable-suggestions');
        if (!suggestionBox) {
            suggestionBox = document.createElement('div');
            suggestionBox.id = 'variable-suggestions';
            suggestionBox.className = 'list-group position-absolute';
            suggestionBox.style.zIndex = '1000';
            suggestionBox.style.maxHeight = '200px';
            suggestionBox.style.overflow = 'auto';
            document.body.appendChild(suggestionBox);
        }
        
        // Positionner la box
        const rect = inputElement.getBoundingClientRect();
        suggestionBox.style.top = `${rect.bottom + window.scrollY}px`;
        suggestionBox.style.left = `${rect.left + window.scrollX}px`;
        suggestionBox.style.width = `${rect.width}px`;
        
        suggestionBox.innerHTML = suggestions.map(v => `
            <button type="button" class="list-group-item list-group-item-action" data-key="${v.key}">
                <strong>${v.key}</strong>
                <small class="text-muted d-block">${v.description || ''}</small>
            </button>
        `).join('');
        
        // Gérer les clics sur les suggestions
        suggestionBox.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                const key = btn.dataset.key;
                const currentValue = inputElement.value;
                const newValue = currentValue.substring(0, insertPos) + 
                                `{{${key}}}` + 
                                currentValue.substring(inputElement.selectionStart);
                
                inputElement.value = newValue;
                this.hideSuggestions();
                inputElement.focus();
            });
        });
    },
    
    hideSuggestions() {
        const suggestionBox = document.getElementById('variable-suggestions');
        if (suggestionBox) {
            suggestionBox.remove();
        }
    }
};

// Gestion de la pagination
const Pagination = {
    create(paginationData, onPageChange) {
        const { current_page, total_pages, has_next, has_prev } = paginationData;
        
        const nav = document.createElement('nav');
        const ul = document.createElement('ul');
        ul.className = 'pagination justify-content-center';
        
        // Bouton précédent
        ul.appendChild(this.createPageItem('Précédent', current_page - 1, !has_prev, onPageChange));
        
        // Numéros de pages
        for (let i = 1; i <= total_pages; i++) {
            if (i === 1 || i === total_pages || (i >= current_page - 2 && i <= current_page + 2)) {
                ul.appendChild(this.createPageItem(i, i, false, onPageChange, i === current_page));
            } else if (i === current_page - 3 || i === current_page + 3) {
                ul.appendChild(this.createPageItem('...', null, true, null));
            }
        }
        
        // Bouton suivant
        ul.appendChild(this.createPageItem('Suivant', current_page + 1, !has_next, onPageChange));
        
        nav.appendChild(ul);
        return nav;
    },
    
    createPageItem(text, page, disabled, onClick, active = false) {
        const li = document.createElement('li');
        li.className = `page-item ${disabled ? 'disabled' : ''} ${active ? 'active' : ''}`;
        
        const a = document.createElement('a');
        a.className = 'page-link';
        a.href = '#';
        a.textContent = text;
        
        if (!disabled && onClick) {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                onClick(page);
            });
        }
        
        li.appendChild(a);
        return li;
    }
};

// Utilitaires
const Utils = {
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    confirmDelete(message = 'Êtes-vous sûr de vouloir supprimer cet élément ?') {
        return confirm(message);
    }
};
