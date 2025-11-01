"""Action pour effectuer des conversions de type sur les variables."""
import json
from plugins.actions.action_base import ActionBase


class VarAction(ActionBase):
    """Action pour convertir des variables en différents types."""
    
    # Métadonnées du plugin
    plugin_name = "var"
    label = "Variables (Conversion)"
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

    def execute(self, context):
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
            target_type = context.get('target_type')
            variables = context.get('variables', {})
            
            logs.append(f"Conversion de la variable '{variable_name}' vers le type '{target_type}'")
            
            # Récupérer la valeur de la variable
            if variable_name not in variables:
                logs.append(f"❌ ERREUR : Variable '{variable_name}' introuvable")
                return (1, "\n".join(logs), output_variables)
            
            original_value = variables[variable_name]
            logs.append(f"Valeur originale : {original_value} (type: {type(original_value).__name__})")
            
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
                            return (1, "\n".join(logs), output_variables)
                    elif isinstance(original_value, dict):
                        converted_value = original_value
                    else:
                        logs.append(f"❌ ERREUR : Impossible de convertir {type(original_value).__name__} en dictionnaire")
                        return (1, "\n".join(logs), output_variables)
                    
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
                
                return (0, "\n".join(logs), output_variables)
                
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                logs.append(f"❌ ERREUR de conversion : {str(e)}")
                return (1, "\n".join(logs), output_variables)
                
        except Exception as e:
            logs.append(f"❌ ERREUR inattendue : {str(e)}")
            return (1, "\n".join(logs), output_variables)


# Enregistrement du plugin
def register():
    """Enregistre le plugin VarAction."""
    return VarAction
