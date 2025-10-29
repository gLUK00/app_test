"""Classe de base pour tous les plugins de rapports."""
from abc import abstractmethod
from plugins.plugin_base import PluginBase


class ReportBase(PluginBase):
    """
    Classe de base abstraite pour tous les plugins de rapports.
    Les plugins de rapports permettent de générer différents types de rapports
    (PDF, HTML, Excel, etc.) à partir des résultats de tests.
    """
    
    # Métadonnées du plugin (à surcharger dans les sous-classes)
    plugin_name = None  # Nom unique du plugin de rapport
    
    def __init__(self):
        """Initialise le plugin de rapport."""
        self.report_data = None
    
    @abstractmethod
    def get_metadata(self):
        """
        Retourne les métadonnées du plugin de rapport.
        
        Returns:
            dict: Métadonnées du plugin
        """
        return {
            "name": self.plugin_name or self.__class__.__name__,
            "version": self.version,
            "author": self.author,
            "description": self.__doc__.strip() if self.__doc__ else "",
            "output_format": self.get_output_format()
        }
    
    @abstractmethod
    def validate_config(self, config):
        """
        Valide la configuration du plugin de rapport.
        
        Args:
            config (dict): Configuration à valider
        
        Returns:
            tuple: (bool, str) - (succès, message d'erreur éventuel)
        """
        return (True, "")
    
    @abstractmethod
    def get_output_format(self):
        """
        Retourne le format de sortie du rapport.
        
        Returns:
            str: Format de sortie (pdf, html, excel, json, etc.)
        """
        pass
    
    @abstractmethod
    def get_configuration_schema(self):
        """
        Retourne le schéma de configuration du rapport.
        Permet de définir les options personnalisables du rapport.
        
        Returns:
            list: Liste de champs de configuration
        """
        pass
    
    @abstractmethod
    def generate(self, test_results, config=None):
        """
        Génère le rapport à partir des résultats de tests.
        
        Args:
            test_results (dict): Résultats des tests à inclure dans le rapport
            config (dict): Configuration personnalisée pour le rapport
        
        Returns:
            dict: Résultat de la génération
            {
                "success": True/False,
                "message": "Message de succès ou d'erreur",
                "file_path": "Chemin vers le fichier généré",
                "data": "Données du rapport (si applicable)"
            }
        """
        pass
    
    def set_data(self, data):
        """Définit les données du rapport."""
        self.report_data = data
    
    def get_supported_templates(self):
        """
        Retourne la liste des modèles de rapport supportés.
        
        Returns:
            list: Liste des noms de modèles disponibles
        """
        return ["default"]
