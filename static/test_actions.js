/**
 * Gestionnaire d'actions pour les tests
 * Fichier mutualisé entre test_add.html et test_edit.html
 */

class TestActionsManager {
    constructor() {
        this.actionMasks = {};
        this.actionOutputVariables = {};
        this.actionLabels = {};
        this.actions = [];
        this.variables = [];
        this.editingActionIndex = -1;
        this.actionModal = null;
        this.variableModal = null;
    }

    /**
     * Charge les masques de saisie depuis l'API et génère les labels dynamiquement
     */
    async loadActionMasks() {
        try {
            const result = await API.get('/api/actions/masks');
            this.actionMasks = result;
            
            // Charger les labels depuis l'API
            await this.loadActionLabels();
            
            // Alimenter dynamiquement le select actionType
            this.populateActionTypeSelect();
        } catch (error) {
            console.error('Erreur lors du chargement des masques:', error);
            Notification.error('Erreur lors du chargement des types d\'actions');
        }
    }

    /**
     * Charge les labels d'affichage depuis l'API
     */
    async loadActionLabels() {
        try {
            const labels = await API.get('/api/actions/labels');
            this.actionLabels = labels;
        } catch (error) {
            console.error('Erreur lors du chargement des labels:', error);
            // Fallback : générer les labels automatiquement
            this.generateActionLabels();
        }
    }

    /**
     * Génère les labels d'affichage pour chaque type d'action (fallback)
     */
    generateActionLabels() {
        // Générer les labels automatiquement si l'API n'est pas disponible
        Object.keys(this.actionMasks).forEach(actionType => {
            if (!this.actionLabels[actionType]) {
                // Capitaliser la première lettre de chaque mot séparé par underscore ou tiret
                this.actionLabels[actionType] = actionType
                    .split(/[_-]/)
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
            }
        });
    }

    /**
     * Peuple dynamiquement le select des types d'action
     */
    populateActionTypeSelect() {
        const actionTypeSelect = document.getElementById('actionType');
        if (!actionTypeSelect) return;
        
        // Vider le select sauf l'option par défaut
        actionTypeSelect.innerHTML = '<option value="">-- Sélectionner un type --</option>';
        
        // Ajouter les options dynamiquement, triées par label
        const sortedTypes = Object.keys(this.actionMasks).sort((a, b) => {
            return this.actionLabels[a].localeCompare(this.actionLabels[b]);
        });

        sortedTypes.forEach(actionType => {
            const option = document.createElement('option');
            option.value = actionType;
            option.textContent = this.actionLabels[actionType];
            actionTypeSelect.appendChild(option);
        });
    }

    /**
     * Charge les variables de sortie depuis l'API
     */
    async loadActionOutputVariables() {
        try {
            const result = await API.get('/api/actions/output-variables');
            this.actionOutputVariables = result;
            console.log('Action output variables chargées:', this.actionOutputVariables);
        } catch (error) {
            console.error('Erreur lors du chargement des variables de sortie:', error);
        }
    }

    /**
     * Crée un champ de formulaire dynamiquement
     */
    createFormField(field) {
        const divWrapper = document.createElement('div');
        divWrapper.className = 'mb-3';
        
        const label = document.createElement('label');
        label.className = 'form-label';
        label.setAttribute('for', field.name);
        label.textContent = field.label + (field.required ? ' *' : '');
        divWrapper.appendChild(label);
        
        let input;
        
        if (field.type === 'select') {
            input = document.createElement('select');
            input.className = 'form-select';
            
            // Option par défaut
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = '-- Sélectionner --';
            input.appendChild(defaultOption);
            
            // Ajouter les options
            field.options.forEach(option => {
                const opt = document.createElement('option');
                // Gérer à la fois les strings simples et les objets {value, label}
                if (typeof option === 'object' && option.value !== undefined) {
                    opt.value = option.value;
                    opt.textContent = option.label || option.value;
                } else {
                    opt.value = option;
                    opt.textContent = option;
                }
                input.appendChild(opt);
            });
        } else if (field.type === 'select-var-test') {
            // Nouveau type : sélection parmi les variables du test
            input = document.createElement('select');
            input.className = 'form-select';
            
            // Option par défaut
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = '-- Sélectionner une variable --';
            input.appendChild(defaultOption);
            
            // Ajouter les variables du test
            this.variables.forEach(variable => {
                const opt = document.createElement('option');
                opt.value = variable;
                opt.textContent = variable;
                input.appendChild(opt);
            });
        } else if (field.type === 'textarea') {
            input = document.createElement('textarea');
            input.className = 'form-control';
            input.rows = 3;
        } else if (field.type === 'number') {
            input = document.createElement('input');
            input.type = 'number';
            input.className = 'form-control';
        } else {
            // Par défaut, input text
            input = document.createElement('input');
            input.type = field.type === 'string' ? 'text' : field.type;
            input.className = 'form-control';
        }
        
        input.id = field.name;
        input.name = field.name;
        
        if (field.placeholder) {
            input.placeholder = field.placeholder;
        }
        
        if (field.required) {
            input.required = true;
        }
        
        divWrapper.appendChild(input);
        
        // Ajouter un texte d'aide si nécessaire
        if (field.name === 'headers' || field.name === 'body') {
            const small = document.createElement('small');
            small.className = 'form-text text-muted';
            small.textContent = 'Format JSON valide';
            divWrapper.appendChild(small);
        }
        
        return divWrapper;
    }

    /**
     * Affiche les champs dynamiques selon le type sélectionné
     */
    displayDynamicFields(actionType, currentParameters = {}) {
        const dynamicFieldsContainer = document.getElementById('dynamicFields');
        dynamicFieldsContainer.innerHTML = '';
        
        if (!actionType || !this.actionMasks[actionType]) {
            document.getElementById('outputVariablesSection').style.display = 'none';
            return;
        }
        
        const mask = this.actionMasks[actionType];
        mask.forEach(field => {
            const fieldElement = this.createFormField(field);
            dynamicFieldsContainer.appendChild(fieldElement);
            
            // Remplir avec les valeurs existantes si on édite
            if (currentParameters && currentParameters[field.name]) {
                const input = fieldElement.querySelector(`#${field.name}`);
                if (input) {
                    const value = currentParameters[field.name];
                    if (typeof value === 'object') {
                        input.value = JSON.stringify(value, null, 2);
                    } else {
                        input.value = value;
                    }
                }
            }
        });
        
        // Afficher les variables de sortie disponibles
        this.displayOutputVariables(actionType, currentParameters.output_mapping || {});
    }

    /**
     * Affiche les variables de sortie disponibles
     */
    displayOutputVariables(actionType, currentMapping = {}) {
        const outputSection = document.getElementById('outputVariablesSection');
        const outputList = document.getElementById('outputVariablesList');
        
        if (!actionType || !this.actionOutputVariables[actionType] || this.actionOutputVariables[actionType].length === 0) {
            outputSection.style.display = 'none';
            return;
        }
        
        outputSection.style.display = 'block';
        outputList.innerHTML = '';
        
        const outputVars = this.actionOutputVariables[actionType];
        outputVars.forEach(outputVar => {
            const div = document.createElement('div');
            div.className = 'mb-3 p-3 border rounded';
            
            let html = `
                <div class="form-check mb-2">
                    <input class="form-check-input output-var-checkbox" type="checkbox" 
                           id="output_${outputVar.name}" 
                           data-var-name="${outputVar.name}"
                           ${currentMapping[outputVar.name] ? 'checked' : ''}>
                    <label class="form-check-label fw-bold" for="output_${outputVar.name}">
                        ${outputVar.name}
                    </label>
                </div>
                <small class="text-muted d-block mb-2">${outputVar.description}</small>
                <div class="output-mapping-section" id="mapping_${outputVar.name}" 
                     style="display: ${currentMapping[outputVar.name] ? 'block' : 'none'};">
                    <label class="form-label small">Mapper à la variable du test:</label>
                    <select class="form-select form-select-sm output-var-mapping" 
                            data-var-name="${outputVar.name}">
                        <option value="">-- Sélectionner une variable --</option>
                        ${this.variables.map(v => `<option value="${v}" ${currentMapping[outputVar.name] === v ? 'selected' : ''}>${v}</option>`).join('')}
                    </select>
                </div>
            `;
            
            div.innerHTML = html;
            outputList.appendChild(div);
            
            // Gérer l'affichage du mapping
            const checkbox = div.querySelector('.output-var-checkbox');
            const mappingSection = div.querySelector('.output-mapping-section');
            
            checkbox.addEventListener('change', (e) => {
                mappingSection.style.display = e.target.checked ? 'block' : 'none';
            });
        });
    }

    /**
     * Formate et affiche les données "value" de manière indentée
     */
    formatActionValue(value) {
        if (!value || typeof value !== 'object' || Object.keys(value).length === 0) {
            return '';
        }
        
        let html = '<div class="mt-2" style="font-size: 0.85rem;">';
        html += '<div class="text-muted mb-1"><strong>Paramètres :</strong></div>';
        html += '<div style="font-family: monospace; background-color: #f8f9fa; padding: 8px; border-radius: 4px; border-left: 3px solid #0d6efd;">';
        
        for (const [key, val] of Object.entries(value)) {
            // Exclure output_mapping de l'affichage car ce n'est pas un paramètre de l'action
            if (key === 'output_mapping') {
                continue;
            }
            
            if (val !== null && val !== undefined && val !== '') {
                let displayValue = val;
                
                // Formater les objets JSON
                if (typeof val === 'object') {
                    displayValue = JSON.stringify(val, null, 2);
                    html += `<div style="margin-bottom: 6px;">`;
                    html += `<span style="color: #0d6efd; font-weight: 500;">${key}:</span>`;
                    html += `<pre style="margin: 2px 0 0 20px; font-size: 0.8rem; color: #495057;">${displayValue}</pre>`;
                    html += `</div>`;
                } else {
                    // Tronquer les valeurs trop longues
                    if (typeof displayValue === 'string' && displayValue.length > 100) {
                        displayValue = displayValue.substring(0, 100) + '...';
                    }
                    html += `<div style="margin-bottom: 4px; margin-left: 0px;">`;
                    html += `<span style="color: #0d6efd; font-weight: 500;">${key}:</span> `;
                    html += `<span style="color: #495057;">${displayValue}</span>`;
                    html += `</div>`;
                }
            }
        }
        
        html += '</div></div>';
        return html;
    }

    /**
     * Affiche la liste des actions
     */
    renderActionsList() {
        const actionsList = document.getElementById('actionsList');
        
        if (this.actions.length === 0) {
            actionsList.innerHTML = '<p class="text-muted text-center">Aucune action ajoutée. Cliquez sur "Ajouter une action" pour commencer.</p>';
            return;
        }
        
        actionsList.innerHTML = this.actions.map((action, index) => {
            // Récupérer les variables de sortie mappées pour cette action
            let outputBadges = '';
            if (action.value && action.value.output_mapping && Object.keys(action.value.output_mapping).length > 0) {
                const outputMapping = action.value.output_mapping;
                
                outputBadges = Object.entries(outputMapping).map(([outputVar, testVar]) => {
                    // Vérifier si la variable du test existe toujours dans la liste des variables du test
                    const isTestVarDefined = this.variables.includes(testVar);
                    const badgeColor = isTestVarDefined ? 'success' : 'secondary';
                    
                    return `<span class="badge bg-${badgeColor} me-1" style="font-size: 0.75rem;">${outputVar} → ${testVar}</span>`;
                }).join('');
            }
            
            const actionLabel = this.actionLabels[action.type] || action.type.toUpperCase();
            
            return `
            <div class="card mb-2 action-item" data-index="${index}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="d-flex align-items-center justify-content-between mb-2">
                                <div class="d-flex align-items-center">
                                    <span class="badge bg-secondary me-2">#${index + 1}</span>
                                    <h6 class="mb-0">Action ${actionLabel}</h6>
                                    <span class="badge bg-primary ms-2">${actionLabel}</span>
                                </div>
                                ${outputBadges ? `<div class="d-flex align-items-center flex-wrap">${outputBadges}</div>` : ''}
                            </div>
                            ${this.formatActionValue(action.value)}
                        </div>
                        <div class="btn-group ms-3" style="flex-shrink: 0;">
                            ${index > 0 ? `<button class="btn btn-sm btn-outline-secondary" onclick="testActionsManager.moveAction(${index}, -1)" title="Monter">
                                <i class="fas fa-arrow-up"></i>
                            </button>` : ''}
                            ${index < this.actions.length - 1 ? `<button class="btn btn-sm btn-outline-secondary" onclick="testActionsManager.moveAction(${index}, 1)" title="Descendre">
                                <i class="fas fa-arrow-down"></i>
                            </button>` : ''}
                            <button class="btn btn-sm btn-outline-primary" onclick="testActionsManager.editAction(${index})" title="Modifier">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="testActionsManager.deleteAction(${index})" title="Supprimer">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        }).join('');
    }

    /**
     * Ouvre le modal pour ajouter une action
     */
    openAddActionModal() {
        this.editingActionIndex = -1;
        document.getElementById('actionModalTitle').textContent = 'Ajouter une action';
        document.getElementById('actionForm').reset();
        document.getElementById('dynamicFields').innerHTML = '';
        document.getElementById('outputVariablesSection').style.display = 'none';
        this.actionModal.show();
    }

    /**
     * Édite une action existante
     */
    editAction(index) {
        this.editingActionIndex = index;
        const action = this.actions[index];
        
        document.getElementById('actionModalTitle').textContent = 'Modifier l\'action';
        document.getElementById('actionType').value = action.type;
        
        this.displayDynamicFields(action.type, action.value);
        this.actionModal.show();
    }

    /**
     * Supprime une action
     */
    deleteAction(index) {
        if (confirm('Êtes-vous sûr de vouloir supprimer cette action ?')) {
            this.actions.splice(index, 1);
            this.renderActionsList();
            Notification.success('Action supprimée');
        }
    }

    /**
     * Déplace une action
     */
    moveAction(index, direction) {
        const newIndex = index + direction;
        if (newIndex < 0 || newIndex >= this.actions.length) return;
        
        const temp = this.actions[index];
        this.actions[index] = this.actions[newIndex];
        this.actions[newIndex] = temp;
        
        this.renderActionsList();
    }

    /**
     * Sauvegarde l'action (ajout ou modification)
     */
    saveAction() {
        const actionType = document.getElementById('actionType').value;
        
        if (!actionType) {
            Notification.error('Veuillez sélectionner un type d\'action');
            return;
        }
        
        // Collecter les données du formulaire
        const actionData = {};
        const dynamicFields = document.getElementById('dynamicFields');
        const inputs = dynamicFields.querySelectorAll('input, select, textarea');
        
        // Vérifier les champs requis
        let allRequiredFilled = true;
        inputs.forEach(input => {
            if (input.required && !input.value.trim()) {
                allRequiredFilled = false;
            }
        });
        
        if (!allRequiredFilled) {
            Notification.error('Veuillez remplir tous les champs obligatoires');
            return;
        }
        
        inputs.forEach(input => {
            const value = input.value.trim();
            if (value) {
                // Essayer de parser le JSON si le champ contient du JSON
                if ((input.name === 'headers' || input.name === 'body') && value) {
                    try {
                        actionData[input.name] = JSON.parse(value);
                    } catch (error) {
                        actionData[input.name] = value;
                    }
                } else if (input.type === 'number') {
                    actionData[input.name] = parseInt(value);
                } else {
                    actionData[input.name] = value;
                }
            }
        });
        
        // Récupérer le mapping des variables de sortie
        const outputMapping = {};
        document.querySelectorAll('.output-var-checkbox:checked').forEach(checkbox => {
            const varName = checkbox.dataset.varName;
            const mappingSelect = document.querySelector(`.output-var-mapping[data-var-name="${varName}"]`);
            if (mappingSelect && mappingSelect.value) {
                outputMapping[varName] = mappingSelect.value;
            }
        });
        
        if (Object.keys(outputMapping).length > 0) {
            actionData.output_mapping = outputMapping;
        }
        
        const action = {
            type: actionType,
            value: actionData
        };
        
        if (this.editingActionIndex >= 0) {
            this.actions[this.editingActionIndex] = action;
            Notification.success('Action modifiée avec succès');
        } else {
            this.actions.push(action);
            Notification.success('Action ajoutée avec succès');
        }
        
        this.renderActionsList();
        this.actionModal.hide();
    }

    /**
     * Affiche la liste des variables
     */
    renderVariablesList() {
        const variablesList = document.getElementById('variablesList');
        
        if (this.variables.length === 0) {
            variablesList.innerHTML = '';
            return;
        }
        
        let html = '<div class="mb-3">';
        html += '<div class="text-muted mb-2"><strong>Variables associées :</strong></div>';
        html += '<div class="d-flex flex-wrap gap-2">';
        
        this.variables.forEach((variable, index) => {
            html += `
                <span class="badge bg-info d-flex align-items-center" style="font-size: 0.9rem; padding: 0.5rem 0.7rem;">
                    <i class="fas fa-tag me-2"></i>
                    ${variable}
                    <button type="button" class="btn-close btn-close-white ms-2" 
                            onclick="testActionsManager.removeVariable(${index})" 
                            style="font-size: 0.6rem;"
                            title="Supprimer"></button>
                </span>
            `;
        });
        
        html += '</div></div>';
        variablesList.innerHTML = html;
        
        // Mettre à jour les suggestions d'autocomplétion
        this.updateTestVariablesSuggestions();
    }

    /**
     * Ouvre le modal pour ajouter une variable
     */
    openAddVariableModal() {
        document.getElementById('variableForm').reset();
        this.variableModal.show();
    }

    /**
     * Sauvegarde une variable
     */
    saveVariable() {
        const variableName = document.getElementById('variableName').value.trim();
        
        if (!variableName) {
            Notification.error('Veuillez saisir un nom de variable');
            return;
        }
        
        // Validation alphanumérique
        const alphanumRegex = /^[a-zA-Z0-9_]+$/;
        if (!alphanumRegex.test(variableName)) {
            Notification.error('Le nom de la variable doit contenir uniquement des caractères alphanumériques et underscore');
            return;
        }
        
        // Vérifier si la variable existe déjà
        if (this.variables.includes(variableName)) {
            Notification.error('Cette variable existe déjà');
            return;
        }
        
        this.variables.push(variableName);
        this.renderVariablesList();
        this.renderActionsList(); // Actualiser les badges de variables de sortie
        this.variableModal.hide();
        Notification.success('Variable ajoutée avec succès');
    }

    /**
     * Supprime une variable
     */
    removeVariable(index) {
        if (confirm('Êtes-vous sûr de vouloir supprimer cette variable ?')) {
            this.variables.splice(index, 1);
            this.renderVariablesList();
            this.renderActionsList(); // Actualiser les badges de variables de sortie
            Notification.success('Variable supprimée');
        }
    }

    /**
     * Met à jour les suggestions de variables du test dans l'autocomplétion
     */
    updateTestVariablesSuggestions() {
        if (window.variableAutocomplete) {
            window.variableAutocomplete.setVariables('test', this.variables);
        }
    }

    /**
     * Initialise les event listeners
     */
    initEventListeners() {
        // Écouter le changement du type d'action
        const actionTypeSelect = document.getElementById('actionType');
        if (actionTypeSelect) {
            actionTypeSelect.addEventListener('change', (e) => {
                this.displayDynamicFields(e.target.value);
            });
        }

        // Bouton d'ajout d'action
        const addActionBtn = document.getElementById('addActionBtn');
        if (addActionBtn) {
            addActionBtn.addEventListener('click', () => this.openAddActionModal());
        }

        // Bouton de sauvegarde d'action
        const saveActionBtn = document.getElementById('saveActionBtn');
        if (saveActionBtn) {
            saveActionBtn.addEventListener('click', () => this.saveAction());
        }

        // Bouton d'ajout de variable
        const addVariableBtn = document.getElementById('addVariableBtn');
        if (addVariableBtn) {
            addVariableBtn.addEventListener('click', () => this.openAddVariableModal());
        }

        // Bouton de sauvegarde de variable
        const saveVariableBtn = document.getElementById('saveVariableBtn');
        if (saveVariableBtn) {
            saveVariableBtn.addEventListener('click', () => this.saveVariable());
        }
    }

    /**
     * Initialise le gestionnaire
     */
    async init() {
        this.actionModal = new bootstrap.Modal(document.getElementById('actionModal'));
        this.variableModal = new bootstrap.Modal(document.getElementById('variableModal'));
        
        await this.loadActionMasks();
        await this.loadActionOutputVariables();
        
        this.initEventListeners();
        
        // Initialiser l'autocomplétion des variables
        if (window.VariableAutocomplete) {
            window.variableAutocomplete = new VariableAutocomplete({
                apiEndpoint: '/api/variables?isRoot=true&page_size=100'
            });
        }
        
        // Mettre à jour les suggestions de variables du test
        this.updateTestVariablesSuggestions();
    }
}

// Instance globale
let testActionsManager;
