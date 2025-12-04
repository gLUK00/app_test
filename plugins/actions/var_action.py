"""Action pour effectuer des conversions de type sur les variables."""
import json
from plugins.actions.action_base import ActionBase


class VarAction(ActionBase):
    """Action pour convertir des variables en différents types."""
    
    # Métadonnées du plugin
    plugin_name = "var"
    label = "Variables (Conversion/Valorisation)"
    version = "1.0.0"
    author = "TestGyver Team"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Convertit des variables en différents types (int, float, bool, list, dict, json)"
        }
    
    def validate_config(self, config):
        """Valide la configuration de l'action."""
        required_fields = ['variable_name', 'target_type']
        for field in required_fields:
            if field not in config or not config[field]:
                return (False, f"Le champ '{field}' est obligatoire")
        
        # Vérifier que le type cible est valide
        valid_types = ['int', 'float', 'bool', 'list', 'dict', 'json']
        if config['target_type'] not in valid_types:
            return (False, f"Type cible invalide. Valeurs acceptées : {', '.join(valid_types)}")
        
        return (True, "")
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour la conversion de variables."""
        return [
            {
                "name": "variable_name",
                "type": "select-var-test",
                "label": "Variable à convertir",
                "placeholder": "Sélectionnez une variable du test",
                "required": True
            },
            {
                "name": "default_value",
                "type": "string",
                "label": "Variable par défaut (optionnel)",
                "placeholder": "156.32, true, [1,2,3], {'key':'value'}, etc.",
                "required": False
            },
            {
                "name": "force_valuation",
                "type": "checkbox",
                "label": "Forcer la valorisation (optionnel)",
                "required": False
            },
            {
                "name": "target_type",
                "type": "select",
                "label": "Type cible",
                "options": [
                    {"value": "int", "label": "Entier (int)"},
                    {"value": "float", "label": "Décimal (float)"},
                    {"value": "bool", "label": "Booléen (bool)"},
                    {"value": "list", "label": "Liste (list)"},
                    {"value": "dict", "label": "Dictionnaire (dict)"},
                    {"value": "json", "label": "JSON (string)"}
                ],
                "required": True
            }
        ]
    
    def get_output_variables(self):
        """Retourne la liste des variables de sortie de l'action."""
        return [
            {
                "name": "converted_value",
                "description": "Valeur convertie de la variable"
            }
        ]

    def get_js_show_form(self):
        """
        Retourne le code JavaScript à exécuter lors de l'affichage du formulaire.
        Cette fonction met en évidence la variable sélectionnée si elle n'existe pas.
        """
        return """
// Fonction appelée lors de l'affichage du formulaire
console.log('VarAction: jsShowForm appelée', actionConfig);

// Vérifier si une variable est déjà sélectionnée
const variableSelect = document.getElementById('variable_name');
if (!variableSelect) {
    console.warn('VarAction: Champ variable_name non trouvé');
    return;
}

// Ajouter un écouteur pour mettre à jour le style quand on change la sélection
variableSelect.addEventListener('change', function() {
    const selectedValue = this.value;
    if (!selectedValue) {
        this.classList.remove('is-valid', 'is-invalid');
        return;
    }
    
    // Récupérer la liste des variables du test depuis testActionsManager
    const variables = window.testActionsManager ? window.testActionsManager.variables : [];
    
    if (variables.includes(selectedValue)) {
        this.classList.remove('is-invalid');
        this.classList.add('is-valid');
    } else {
        this.classList.remove('is-valid');
        this.classList.add('is-invalid');
    }
});

// Déclencher la validation initiale si une valeur est déjà sélectionnée
if (actionConfig && actionConfig.variable_name) {
    variableSelect.value = actionConfig.variable_name;
    variableSelect.dispatchEvent(new Event('change'));
}
"""

    def get_js_validate_form(self):
        """
        Retourne le code JavaScript à exécuter lors de la validation du formulaire.
        Cette fonction valide que la variable sélectionnée existe dans les variables du test.
        """
        return """
// Fonction appelée lors de la validation du formulaire
console.log('VarAction: jsValidateForm appelée', actionConfig, variables);

const variableName = actionConfig.variable_name;

// Vérifier que la variable est sélectionnée
if (!variableName || variableName.trim() === '') {
    return {
        isValid: false,
        errorMessage: 'Veuillez sélectionner une variable à convertir'
    };
}

// Vérifier que la variable existe dans la liste des variables du test
if (!variables || !Array.isArray(variables)) {
    console.warn('VarAction: Liste des variables du test non disponible');
    return {
        isValid: true,
        errorMessage: ''
    };
}

if (!variables.includes(variableName)) {
    return {
        isValid: false,
        errorMessage: `La variable "${variableName}" n'existe pas dans les variables du test. Veuillez créer cette variable avant de l'utiliser dans cette action.`
    };
}

// une variable de sortie est obligatoire
if (!actionConfig.output_mapping || Object.keys(actionConfig.output_mapping).length === 0) {
    console.log( 'VarAction: Aucune variable de sortie définie' );
    console.log( actionConfig );
    return {
        isValid: false,
        errorMessage: 'Au moins une variable de sortie doit être définie pour cette action.'
    };
}

// Tout est OK
return {
    isValid: true,
    errorMessage: ''
};
"""

    def execute(self, context, test_variables=None):
        """
        Exécute la conversion de variable.
        
        Args:
            context: Dictionnaire contenant les paramètres de l'action et le contexte d'exécution
                - variable_name: Nom de la variable à convertir
                - target_type: Type cible (int, float, bool, list, dict, json)
                - variables: Dictionnaire des variables disponibles
        
        Returns:
            tuple: (code de sortie, logs d'exécution, variables de sortie)
        """
        logs = []
        output_variables = {}
        
        try:
            variable_name = context.get('variable_name')
            default_value = context.get('default_value')
            target_type = context.get('target_type')
            #variables = context.get('variables', {})
            force_valuation = context.get('force_valuation', False)
            
            logs.append(f"Conversion de la variable '{variable_name}' vers le type '{target_type}'")
            
            # Récupérer la valeur de la variable
            if force_valuation and default_value is not None:
                original_value = default_value
                logs.append(f"Valorisation forcée. Utilisation de la valeur par défaut : {default_value}")
            elif 'app.' + variable_name not in test_variables and default_value is None:
                logs.append(f"❌ ERREUR : Variable '{variable_name}' introuvable")
                return self.get_result( False, None )
            
            elif 'app.' + variable_name in test_variables and test_variables['app.' + variable_name] != None:
                original_value = test_variables['app.' + variable_name]
                logs.append(f"Valeur originale : {original_value} (type: {type(original_value).__name__})")
            else:
                # Utiliser la valeur par défaut
                original_value = default_value
                logs.append(f"Variable '{variable_name}' introuvable. Utilisation de la valeur par défaut : {default_value}")
            
            # Effectuer la conversion
            converted_value = None
            
            try:
                if target_type == 'int':
                    converted_value = int(original_value)
                    
                elif target_type == 'float':
                    converted_value = float(original_value)
                    
                elif target_type == 'bool':
                    # Gestion intelligente de la conversion en booléen
                    if isinstance(original_value, str):
                        converted_value = original_value.lower() in ('true', '1', 'yes', 'oui', 'y', 'o')
                    else:
                        converted_value = bool(original_value)
                    
                elif target_type == 'list':
                    if isinstance(original_value, str):
                        # Si c'est une string JSON, essayer de la parser
                        try:
                            parsed = json.loads(original_value)
                            if isinstance(parsed, list):
                                converted_value = parsed
                            else:
                                # Si ce n'est pas une liste, créer une liste avec cet élément
                                converted_value = [parsed]
                        except json.JSONDecodeError:
                            # Si ce n'est pas du JSON, créer une liste avec la string
                            converted_value = [original_value]
                    elif isinstance(original_value, (list, tuple)):
                        converted_value = list(original_value)
                    else:
                        # Créer une liste avec la valeur
                        converted_value = [original_value]
                    
                elif target_type == 'dict':
                    if isinstance(original_value, str):
                        # Si c'est une string JSON, essayer de la parser
                        converted_value = json.loads(original_value)
                        if not isinstance(converted_value, dict):
                            logs.append(f"❌ ERREUR : La valeur parsée n'est pas un dictionnaire")
                            return self.get_result( False, None )
                    elif isinstance(original_value, dict):
                        converted_value = original_value
                    else:
                        logs.append(f"❌ ERREUR : Impossible de convertir {type(original_value).__name__} en dictionnaire")
                        return self.get_result( False, None )
                    
                elif target_type == 'json':
                    # Convertir en string JSON
                    if isinstance(original_value, str):
                        # Vérifier que c'est du JSON valide
                        json.loads(original_value)
                        converted_value = original_value
                    else:
                        converted_value = json.dumps(original_value, ensure_ascii=False, indent=2)
                
                logs.append(f"✅ Conversion réussie : {converted_value} (type: {type(converted_value).__name__})")
                output_variables['converted_value'] = converted_value
                
                return self.get_result(True, output_variables)
                
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                logs.append(f"❌ ERREUR de conversion : {str(e)}")
                return self.get_result( False, None )
                
        except Exception as e:
            logs.append(f"❌ ERREUR inattendue : {str(e)}")
            return self.get_result( False, None )


# Enregistrement du plugin
def register():
    """Enregistre le plugin VarAction."""
    return VarAction
