"""Action pour effectuer une pause."""
import time
from plugins.actions.action_base import ActionBase


class PauseAction(ActionBase):
    """Action pour effectuer une pause dans l'exécution du test."""
    
    # Métadonnées du plugin
    plugin_name = "pause"
    label = "Pause"
    version = "1.0.0"
    author = "TestGyver Team"
    color = "#0dcaf0"
    
    def get_metadata(self):
        """Retourne les métadonnées de l'action."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Effectue une pause dans l'exécution du test",
            "color": self.color
        }
    
    def validate_config(self, config):
        """Valide la configuration de l'action."""
        if 'duration' not in config:
            return (False, "La durée de la pause est obligatoire")
        
        try:
            duration = int(config['duration'])
            if duration < 0:
                return (False, "La durée de la pause doit être positive")
        except ValueError:
            return (False, "La durée de la pause doit être un nombre entier")
            
        return (True, "")
    
    def get_input_mask(self):
        """Retourne le masque de saisie pour l'action Pause."""
        return [
            {
                "name": "duration",
                "type": "number",
                "label": "Durée (ms)",
                "placeholder": "20",
                "default": 20,
                "required": True,
                "description": "Durée de la pause en millisecondes"
            },
            {
                "name": "message",
                "type": "string",
                "label": "Message (optionnel)",
                "placeholder": "Pause avant la prochaine étape...",
                "required": False,
                "description": "Message à afficher dans les logs avant la pause"
            }
        ]
    
    def get_output_variables(self):
        """Retourne la liste des variables de sortie."""
        return []
    
    def execute(self, config, context=None):
        """
        Exécute l'action de pause.
        
        Args:
            config (dict): Configuration de l'action
            context (dict): Contexte d'exécution (variables, etc.)
            
        Returns:
            dict: Résultat de l'exécution
        """
        self.traces = []
        
        try:
            # Récupération de la durée (défaut 20ms)
            duration_ms = int(config.get('duration', 20))
            message = config.get('message', '')
            
            # Affichage du message si présent
            if message:
                self.traces.append(f"Message: {message}")
            
            self.traces.append(f"Pause de {duration_ms} ms...")
            
            # Conversion en secondes pour time.sleep
            time.sleep(duration_ms / 1000.0)
            
            self.traces.append("Reprise de l'exécution")
            
            return {
                "result": True,
                "message": f"Pause de {duration_ms} ms effectuée",
                "traces": self.traces,
                "output_variables": {}
            }
            
        except Exception as e:
            return {
                "result": False,
                "message": f"Erreur lors de la pause: {str(e)}",
                "traces": self.traces,
                "output_variables": {}
            }
