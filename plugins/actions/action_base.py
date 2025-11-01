"""Classe de base pour toutes les actions."""
from abc import abstractmethod
from plugins.plugin_base import PluginBase


class ActionBase(PluginBase):
    """
    Classe de base abstraite pour toutes les actions.
    Chaque action doit hériter de cette classe et implémenter les méthodes requises.
    """
    
    # Métadonnées du plugin (à surcharger dans les sous-classes)
    plugin_name = None  # Nom unique de l'action (ex: 'http', 'ssh', etc.)
    label = None  # Label d'affichage (ex: 'HTTP Request', 'I/O (Fichiers)', etc.)
    
    def __init__(self):
        """Initialise l'action."""
        self.code = 0
        self.traces = []
    
    @abstractmethod
    def get_metadata(self):
        """
        Retourne les métadonnées de l'action.
        
        Returns:
            dict: Métadonnées de l'action
        """
        return {
            "name": self.plugin_name or self.__class__.__name__,
            "version": self.version,
            "author": self.author,
            "description": self.__doc__.strip() if self.__doc__ else ""
        }
    
    @abstractmethod
    def validate_config(self, config):
        """
        Valide la configuration de l'action.
        
        Args:
            config (dict): Configuration à valider
        
        Returns:
            tuple: (bool, str) - (succès, message d'erreur éventuel)
        """
        return (True, "")
    
    @abstractmethod
    def get_input_mask(self):
        """
        Retourne le masque de saisie pour les paramètres de l'action.
        
        Returns:
            list: Liste de dictionnaires définissant les champs du formulaire
            Exemple:
            [
                {
                    "name": "url",
                    "type": "string",
                    "label": "URL",
                    "placeholder": "https://example.com",
                    "required": True
                }
            ]
        """
        pass
    
    @abstractmethod
    def get_output_variables(self):
        """
        Retourne la liste des variables de sortie possibles pour cette action.
        Ces variables pourront être utilisées dans les actions suivantes du même test.
        
        Returns:
            list: Liste de dictionnaires définissant les variables de sortie
            Exemple:
            [
                {
                    "name": "response_status",
                    "description": "Code de statut HTTP de la réponse",
                    "type": "number"
                },
                {
                    "name": "response_body",
                    "description": "Corps de la réponse",
                    "type": "string"
                }
            ]
        """
        pass
    
    @abstractmethod
    def execute(self, action_context):
        """
        Exécute l'action avec le contexte fourni.
        
        Args:
            action_context: Dictionnaire contenant les paramètres de l'action
        
        Returns:
            dict: Résultat de l'exécution avec le code et les traces
            {
                "code": 0,  # 0 = succès, autre = erreur
                "traces": ["trace1", "trace2", ...],
                "result": {}  # Données optionnelles de résultat
            }
        """
        
        print( "Exécution de l'action de base - à surcharger dans les sous-classes" )
        
        
        pass
    
    def add_trace(self, message):
        """Ajoute une trace d'exécution."""
        self.traces.append(message)
    
    def set_code(self, code):
        """Définit le code de retour."""
        self.code = code
    
    def get_result(self, result_data=None, output_variables=None):
        """
        Retourne le résultat formaté de l'action.
        
        Args:
            result_data: Données optionnelles à inclure dans le résultat
            output_variables: Dictionnaire des variables de sortie avec leurs valeurs
        
        Returns:
            dict: Résultat formaté
        """
        output = {
            "code": self.code,
            "traces": self.traces
        }
        
        if result_data is not None:
            output["result"] = result_data
        
        if output_variables is not None:
            output["output_variables"] = output_variables
        
        return output
