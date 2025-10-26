"""Classe de base pour toutes les actions."""
from abc import ABC, abstractmethod

class ActionBase(ABC):
    """
    Classe de base abstraite pour toutes les actions.
    Chaque action doit hériter de cette classe et implémenter les méthodes requises.
    """
    
    def __init__(self):
        """Initialise l'action."""
        self.code = 0
        self.traces = []
    
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
        pass
    
    def add_trace(self, message):
        """Ajoute une trace d'exécution."""
        self.traces.append(message)
    
    def set_code(self, code):
        """Définit le code de retour."""
        self.code = code
    
    def get_result(self, result_data=None):
        """
        Retourne le résultat formaté de l'action.
        
        Args:
            result_data: Données optionnelles à inclure dans le résultat
        
        Returns:
            dict: Résultat formaté
        """
        output = {
            "code": self.code,
            "traces": self.traces
        }
        
        if result_data is not None:
            output["result"] = result_data
        
        return output
